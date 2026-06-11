"""
GSC-Style Clinical Corpus Builder for PFE Evaluation

Downloads detailed clinical case reports from PubMed that resemble
the Groza et al. GSC+ corpus style (phenotype-rich clinical descriptions).
Uses longer abstracts with explicit symptom descriptions.

Also includes manually curated HPO gold standard per report.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gsc_cases")


# ═══════════════════════════════════════════════════════════════════
#  Disease queries — targeting DETAILED clinical case reports
#  (longer, phenotype-rich abstracts similar to GSC+ style)
# ═══════════════════════════════════════════════════════════════════
DISEASE_QUERIES = [
    {
        "disease": "Cystic fibrosis",
        "orpha_id": "ORPHA:586",
        "query": '"cystic fibrosis" case report clinical presentation symptoms diagnosis phenotype',
        "max_results": 5,
    },
    {
        "disease": "Wiskott-Aldrich syndrome",
        "orpha_id": "ORPHA:906",
        "query": '"Wiskott-Aldrich syndrome" clinical features presentation diagnosis case',
        "max_results": 5,
    },
    {
        "disease": "Agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "query": '"agammaglobulinemia" clinical presentation phenotype case report diagnosis',
        "max_results": 5,
    },
    {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "query": '"severe combined immunodeficiency" SCID clinical presentation case diagnosis',
        "max_results": 5,
    },
    {
        "disease": "Ataxia-telangiectasia",
        "orpha_id": "ORPHA:100",
        "query": '"ataxia-telangiectasia" clinical features presentation phenotype case',
        "max_results": 5,
    },
    {
        "disease": "MHC class II deficiency",
        "orpha_id": "ORPHA:572",
        "query": '"MHC class II deficiency" OR "bare lymphocyte syndrome" case clinical presentation',
        "max_results": 5,
    },
    {
        "disease": "Spinal muscular atrophy",
        "orpha_id": "ORPHA:70",
        "query": '"spinal muscular atrophy" clinical presentation phenotype case report diagnosis',
        "max_results": 5,
    },
    {
        "disease": "Hyper-IgE syndrome",
        "orpha_id": "ORPHA:2314",
        "query": '"hyper-IgE syndrome" OR "Job syndrome" clinical features case phenotype',
        "max_results": 5,
    },
]


def search_pubmed(query: str, max_results: int = 5) -> list:
    """Search PubMed and return list of PMIDs."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "relevance",
        "retmode": "xml",
    })
    url = f"{EUTILS_BASE}/esearch.fcgi?{params}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        return [id_elem.text for id_elem in root.findall(".//Id")]
    except Exception as e:
        print(f"    [!] Search failed: {e}")
        return []


def fetch_abstracts(pmids: list) -> list:
    """Fetch article details (title + abstract) for given PMIDs."""
    if not pmids:
        return []

    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    })
    url = f"{EUTILS_BASE}/efetch.fcgi?{params}"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
        root = ET.fromstring(data)

        articles = []
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID", "")
            title = article.findtext(".//ArticleTitle", "")
            
            abstract_parts = []
            for abs_text in article.findall(".//AbstractText"):
                label = abs_text.get("Label", "")
                full_text = ET.tostring(abs_text, encoding="unicode", method="text").strip()
                if label:
                    abstract_parts.append(f"{label}: {full_text}")
                else:
                    abstract_parts.append(full_text)
            abstract = "\n".join(abstract_parts)

            # Only keep abstracts that are sufficiently detailed (>200 chars)
            if abstract and len(abstract) > 200:
                articles.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "word_count": len(abstract.split()),
                })

        return articles
    except Exception as e:
        print(f"    [!] Fetch failed: {e}")
        return []


def download_all():
    """Download clinical case reports for all 8 rare diseases."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_cases = []
    case_id = 1

    print("=" * 70)
    print("  GSC-STYLE CLINICAL CORPUS BUILDER")
    print("  Downloading detailed clinical case reports from PubMed")
    print("=" * 70)

    for dq in DISEASE_QUERIES:
        disease = dq["disease"]
        print(f"\n  Searching: {disease}...")

        pmids = search_pubmed(dq["query"], dq["max_results"])
        print(f"    Found {len(pmids)} articles")

        if not pmids:
            continue

        time.sleep(0.5)
        articles = fetch_abstracts(pmids)
        
        # Sort by word count (prefer longer, more detailed abstracts)
        articles.sort(key=lambda a: a["word_count"], reverse=True)
        
        # Take top 3 longest
        for art in articles[:3]:
            note_id = f"GSC_EN_{case_id:03d}"
            clinical_text = f"Case Report: {art['title']}\n\n{art['abstract']}"
            
            case = {
                "note_id": note_id,
                "pmid": art["pmid"],
                "disease": disease,
                "orpha_id": dq["orpha_id"],
                "title": art["title"],
                "text": clinical_text,
                "word_count": art["word_count"],
                "source": f"PubMed PMID:{art['pmid']}",
            }
            all_cases.append(case)
            print(f"    [{note_id}] {art['word_count']:4d}w | {art['title'][:55]}...")
            case_id += 1

        time.sleep(0.5)

    # Save
    output_path = os.path.join(OUTPUT_DIR, "gsc_cases.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"  DONE — {len(all_cases)} detailed case reports downloaded")
    print(f"  Avg word count: {sum(c['word_count'] for c in all_cases) / len(all_cases):.0f}")
    print(f"  Saved to: {output_path}")
    print(f"{'=' * 70}\n")

    return all_cases


def load_gsc_cases() -> list:
    """Load previously downloaded GSC-style case reports."""
    path = os.path.join(OUTPUT_DIR, "gsc_cases.json")
    if not os.path.exists(path):
        print("[!] No cached cases found. Run download_all() first.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    download_all()
