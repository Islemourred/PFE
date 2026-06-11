"""
PubMed Rare Disease Case Report Downloader

Downloads real clinical case report abstracts from PubMed for the same
8 rare diseases as CHU Oran — enabling direct FR vs EN comparison.

Source: NCBI PubMed E-utilities API (free, no key needed)
API docs: https://www.ncbi.nlm.nih.gov/books/NBK25500/

Usage:
    python clinical_notes/pubmed_cases.py
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

# ═══════════════════════════════════════════════════════════════════════
#  DISEASE QUERIES — Same 8 diseases as CHU Oran
# ═══════════════════════════════════════════════════════════════════════

DISEASE_QUERIES = [
    {
        "disease": "Cystic fibrosis",
        "orpha_id": "ORPHA:586",
        "query": '"cystic fibrosis" case report clinical',
        "max_results": 3,
    },
    {
        "disease": "Wiskott-Aldrich syndrome",
        "orpha_id": "ORPHA:906",
        "query": '"Wiskott-Aldrich syndrome" case report clinical',
        "max_results": 3,
    },
    {
        "disease": "X-linked agammaglobulinemia",
        "orpha_id": "ORPHA:47",
        "query": '"agammaglobulinemia" case report clinical presentation',
        "max_results": 3,
    },
    {
        "disease": "Severe combined immunodeficiency",
        "orpha_id": "ORPHA:183660",
        "query": '"severe combined immunodeficiency" case report clinical',
        "max_results": 3,
    },
    {
        "disease": "Ataxia-telangiectasia",
        "orpha_id": "ORPHA:100",
        "query": '"ataxia-telangiectasia" case report clinical',
        "max_results": 3,
    },
    {
        "disease": "MHC class II deficiency",
        "orpha_id": "ORPHA:572",
        "query": '"MHC class II deficiency" OR "bare lymphocyte syndrome" case report',
        "max_results": 3,
    },
    {
        "disease": "Spinal muscular atrophy",
        "orpha_id": "ORPHA:70",
        "query": '"spinal muscular atrophy" case report clinical presentation',
        "max_results": 3,
    },
    {
        "disease": "Hyper-IgE syndrome",
        "orpha_id": "ORPHA:2314",
        "query": '"hyper-IgE syndrome" OR "Job syndrome" case report clinical',
        "max_results": 3,
    },
]

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pubmed_cases")


def search_pubmed(query: str, max_results: int = 3) -> list:
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
            # Extract PMID
            pmid = article.findtext(".//PMID", "")

            # Extract title
            title = article.findtext(".//ArticleTitle", "")

            # Extract abstract (may have multiple sections)
            abstract_parts = []
            for abs_text in article.findall(".//AbstractText"):
                label = abs_text.get("Label", "")
                text = abs_text.text or ""
                # Include any tail text from child elements
                full_text = ET.tostring(abs_text, encoding="unicode", method="text").strip()
                if label:
                    abstract_parts.append(f"{label}: {full_text}")
                else:
                    abstract_parts.append(full_text)

            abstract = "\n".join(abstract_parts)

            # Extract journal + year
            journal = article.findtext(".//Journal/Title", "")
            year = article.findtext(".//PubDate/Year", "")
            if not year:
                year = article.findtext(".//PubDate/MedlineDate", "")[:4] if article.findtext(".//PubDate/MedlineDate") else ""

            # Extract authors
            authors = []
            for author in article.findall(".//Author"):
                last = author.findtext("LastName", "")
                first = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{last} {first}".strip())

            if abstract and len(abstract) > 100:
                articles.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "authors": authors[:3],  # First 3 authors
                })

        return articles
    except Exception as e:
        print(f"    [!] Fetch failed: {e}")
        return []


def download_all():
    """Download case reports for all 8 rare diseases."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_cases = []
    case_id = 1

    print("=" * 70)
    print("  PUBMED RARE DISEASE CASE REPORT DOWNLOADER")
    print("  Fetching clinical case reports for English pipeline evaluation")
    print("=" * 70)

    for dq in DISEASE_QUERIES:
        disease = dq["disease"]
        print(f"\n  Searching: {disease}...")

        # Search PubMed
        pmids = search_pubmed(dq["query"], dq["max_results"])
        print(f"    Found {len(pmids)} articles")

        if not pmids:
            continue

        # Fetch abstracts
        time.sleep(0.5)  # Be nice to NCBI
        articles = fetch_abstracts(pmids)
        print(f"    Downloaded {len(articles)} abstracts with clinical text")

        for art in articles:
            note_id = f"PUBMED_EN_{case_id:03d}"

            # Build clinical text: title + abstract (simulates a clinical note)
            clinical_text = f"Case Report: {art['title']}\n\n{art['abstract']}"

            case = {
                "note_id": note_id,
                "pmid": art["pmid"],
                "disease": disease,
                "orpha_id": dq["orpha_id"],
                "title": art["title"],
                "text": clinical_text,
                "source": f"PubMed PMID:{art['pmid']}",
                "journal": art["journal"],
                "year": art["year"],
                "authors": art["authors"],
            }
            all_cases.append(case)
            print(f"    [{note_id}] {art['title'][:60]}...")
            case_id += 1

        time.sleep(0.5)  # Rate limiting

    # Save all cases to JSON
    output_path = os.path.join(OUTPUT_DIR, "pubmed_cases.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_cases, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"  DONE — {len(all_cases)} case reports downloaded")
    print(f"  Saved to: {output_path}")
    print(f"  Diseases covered: {len(set(c['disease'] for c in all_cases))}")
    print(f"{'=' * 70}\n")

    return all_cases


def load_pubmed_cases() -> list:
    """Load previously downloaded PubMed case reports."""
    path = os.path.join(OUTPUT_DIR, "pubmed_cases.json")
    if not os.path.exists(path):
        print(f"[!] No cached cases found. Run download_all() first.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    download_all()
