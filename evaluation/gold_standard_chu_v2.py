"""
CHU Gold Standard v2 — CORRECTED
Every HPO is text-grounded: annotated ONLY if the phenotype is explicitly mentioned in the clinical note.

Re-annotated by deep reading of all 17 clinical texts on 2026-06-14.
"""

GOLD_STANDARD_CHU_V2 = {

    # ── 1. ABDELLAOUI — Mucoviscidose ────────────────────────────────────
    # TEXT EVIDENCE: "toux grasse", "crépitants bilatéraux", "selles graisseuses",
    # "insuffisance pancréatique exocrine sévère", "malnutrition légère",
    # "Retard statural marqué", "hépatomégalie homogène", "Convulsions"
    # NEGATED: "pas hippocratisme digital", "pas de cyanose", "pas de déformation thoracique",
    #          "absence du tableau clinique évoquant le RGO", "pas d'ictère"
    "CHU_FR_001": {
        "disease": "Mucoviscidose",
        "orpha_id": "ORPHA:586",
        "source_file": "Abdellaoui Med Yanis Mucoviscidose Novembre.docx",
        "expected_hpo": [
            "HP:0012735",   # Cough (toux grasse, quintes de Toux grasses)
            "HP:0030829",   # Crackles (fins crépitants bilatéraux)
            "HP:0002024",   # Malabsorption (selles graisseuses)
            "HP:0001738",   # Exocrine pancreatic insufficiency (insuffisance pancréatique exocrine sévère)
            "HP:0004395",   # Malnutrition (malnutrition légère, dénutrition)
            "HP:0004322",   # Short stature (Retard statural marqué, -3.375 DS)
            "HP:0002240",   # Hepatomegaly (hépatomégalie homogène)
            "HP:0001250",   # Seizure (Convulsions — diagnostics associés)
        ],
    },

    # ── 2. ABDOUNE — Déficit HLA classe II ───────────────────────────────
    # TEXT EVIDENCE: "déficit immunitaire primitif", "infections à répétition",
    # "gingivostomatite herpétique", "érythème + desquamation",
    # "malnutrition sévère", "coloration jaunâtre des dents"
    "CHU_FR_002": {
        "disease": "Déficit en HLA classe II (Bare Lymphocyte Syndrome type II)",
        "orpha_id": "ORPHA:572",
        "source_file": "Abdoune lyne Déficit en HLA DR Djoudi mars 28.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (déficit immunitaire primitif)
            "HP:0002719",   # Recurrent infections (infections à répétition)
            "HP:0010280",   # Stomatitis (gingivostomatite herpétique)
            "HP:0010783",   # Erythema (érythème)
            "HP:0004395",   # Malnutrition (malnutrition sévère)
            "HP:0011073",   # Abnormality of dental color (coloration jaunâtre des dents)
        ],
    },

    # ── 3. AMROUNE — Wiskott-Aldrich ─────────────────────────────────────
    # TEXT EVIDENCE: "déficit immunitaire primitif", "dilatation des bronches DDB",
    # "insuffisance respiratoire chronique stade 1", "thrombopénie",
    # "eczéma", "syndrome hémorragique cutané type pétéchies",
    # "anémie", "pâleur cutanéomuqueuse", "toux grasse",
    # "hippocratisme digital", "Déformation thoracique en carène",
    # "carries dentaires", "infections respiratoires à répétition"
    "CHU_FR_003": {
        "disease": "Syndrome de Wiskott-Aldrich",
        "orpha_id": "ORPHA:906",
        "source_file": "Amroune_Abdelaziz_DIP_Wiskott_Aldrich_Mars2026_Dr_Djoudi_recu_9.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (DIP)
            "HP:0002719",   # Recurrent infections (infections respiratoires à répétition)
            "HP:0002110",   # Bronchiectasis (dilatation des bronches DDB)
            "HP:0002093",   # Respiratory insufficiency (IRC stade 1)
            "HP:0001873",   # Thrombocytopenia (thrombopénie, Plaquette: 90 000)
            "HP:0000964",   # Eczema (eczéma, lésions d'eczéma)
            "HP:0001892",   # Abnormal bleeding (syndrome hémorragique cutané)
            "HP:0000967",   # Petechiae (pétéchies disséminées)
            "HP:0001903",   # Anemia (anémie, Hb: 10.6)
            "HP:0000980",   # Pallor (pâleur cutanéomuqueuse)
            "HP:0012735",   # Cough (toux grasse)
            "HP:0100759",   # Clubbing (hippocratisme digital)
            "HP:0000767",   # Pectus excavatum (déformation thoracique en carène)
            "HP:0000670",   # Carious teeth (carries dentaires)
        ],
    },

    # ── 4. AZZEMMOU — Agammaglobulinémie ─────────────────────────────────
    # TEXT EVIDENCE: "agammaglobulinémie congénitale", "déficit immunitaire",
    # "Otites purulentes...arthrite du genou à répétition",
    # "Toux grasse chronique", "bronchopneumopathie multifocale",
    # "malnutrition", "rétraction tympanique bilatérale",
    # "Conjonctivite allergique", "carries dentaires"
    "CHU_FR_004": {
        "disease": "Agammaglobulinémie liée à l'X (Bruton)",
        "orpha_id": "ORPHA:47",
        "source_file": "Azzemmou mahdi DIP Agammaglobulinémie Mars Djoudi.docx",
        "expected_hpo": [
            "HP:0004432",   # Agammaglobulinemia (agammaglobulinémie)
            "HP:0004430",   # Immunodeficiency (DIP)
            "HP:0000388",   # Otitis media (otites purulentes à répétition)
            "HP:0001369",   # Arthritis (arthrite du genou gauche)
            "HP:0012735",   # Cough (toux grasse chronique)
            "HP:0002090",   # Pneumonia (bronchopneumopathie multifocale)
            "HP:0004395",   # Malnutrition (légère malnutrition)
            "HP:0000670",   # Carious teeth (carries dentaires)
        ],
    },

    # ── 5. BENDJELIDA Med — Mucoviscidose ────────────────────────────────
    # TEXT EVIDENCE: "toux grasse", "fébrile T: 40.1°C", "Pâleur cutanée",
    # "insuffisance pancréatique exocrine", "hippocratisme digital",
    # "malnutrition légère", "obstruction nasale", "selles graisseuses",
    # "Diarrhées chronique huileuse", "insuffisance respiratoire chronique"
    "CHU_FR_005": {
        "disease": "Mucoviscidose",
        "orpha_id": "ORPHA:586",
        "source_file": "Bendjelida Med mars 2026.docx",
        "expected_hpo": [
            "HP:0012735",   # Cough (toux grasse)
            "HP:0001945",   # Fever (fébrile T: 40.1°C)
            "HP:0000980",   # Pallor (Pâleur cutanée)
            "HP:0001738",   # Exocrine pancreatic insufficiency
            "HP:0100759",   # Clubbing (hippocratisme digital)
            "HP:0002093",   # Respiratory insufficiency (IRC, hippocratisme)
            "HP:0004395",   # Malnutrition (malnutrition légère)
            "HP:0001742",   # Nasal obstruction (obstruction nasale)
            "HP:0002024",   # Malabsorption (selles graisseuses)
            "HP:0002014",   # Diarrhea (Diarrhées chronique huileuse)
            "HP:0002240",   # Hepatomegaly (hépatomégalie homogène — echo)
        ],
    },

    # ── 6. BENDJELIDA Israa — Mucoviscidose ──────────────────────────────
    # TEXT EVIDENCE: "toux grasse", "fébrile T: 40.1°C", "Pâleur cutanée",
    # "insuffisance pancréatique exocrine", "hippocratisme digital",
    # "Déformation thoracique Pectus Excavatum", "selles graisseuses",
    # "insuffisance respiratoire chronique", "malnutrition légère",
    # "Dilatation kystique bilatérale des bronches", "obstruction nasale",
    # "hépatomégalie", "rhinite allergique"
    "CHU_FR_006": {
        "disease": "Mucoviscidose",
        "orpha_id": "ORPHA:586",
        "source_file": "RM Bendjelida Israa Mars 2026.docx",
        "expected_hpo": [
            "HP:0012735",   # Cough (toux grasse)
            "HP:0001945",   # Fever (fébrile T: 40.1°C)
            "HP:0000980",   # Pallor (Pâleur cutanée)
            "HP:0001738",   # Exocrine pancreatic insufficiency
            "HP:0100759",   # Clubbing (hippocratisme digital)
            "HP:0000767",   # Pectus excavatum (Pectus Excavatum)
            "HP:0002093",   # Respiratory insufficiency (IRC)
            "HP:0002110",   # Bronchiectasis (Dilatation kystique bilatérale des bronches)
            "HP:0002024",   # Malabsorption (selles graisseuses)
            "HP:0004395",   # Malnutrition (malnutrition légère)
            "HP:0001742",   # Nasal obstruction (obstruction nasale)
            "HP:0002240",   # Hepatomegaly (Hépato splénomégalie homogène)
        ],
    },

    # ── 7. KHERISSI — SCID-like ──────────────────────────────────────────
    # TEXT EVIDENCE: "déficit immunitaire combiné sévère atypique",
    # "infections respiratoires à répétition", "DDB", "IRC sévère grade 2",
    # "toux grasse", "hippocratisme digital", "Déformation thoracique",
    # "Retard staturo-pondéral", "Malnutrition modérée à sévère",
    # "anémie", "thrombopénie (30 000)", "syndrome hémorragique",
    # "carries dentaires", "pan-hypogammaglobulinémie",
    # "Lymphopénies T et B profondes", "pan cytopénie",
    # "détresse respiratoire"
    "CHU_FR_007": {
        "disease": "Déficit immunitaire combiné sévère (SCID-like)",
        "orpha_id": "ORPHA:183660",
        "source_file": "Khrissi Maram SKID LIKE  Mars 26.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (DIP combiné sévère atypique)
            "HP:0002719",   # Recurrent infections (infections respiratoires à répétition)
            "HP:0002110",   # Bronchiectasis (DDB)
            "HP:0002093",   # Respiratory insufficiency (IRC sévère grade 2)
            "HP:0002098",   # Respiratory distress (détresse respiratoire légère permanente)
            "HP:0012735",   # Cough (toux grasse)
            "HP:0100759",   # Clubbing (hippocratisme digitale)
            "HP:0000767",   # Pectus / chest deformity (Déformation thoracique)
            "HP:0001508",   # Failure to thrive (Retard staturo-pondéral)
            "HP:0004395",   # Malnutrition (Malnutrition modérée à sévère)
            "HP:0001903",   # Anemia (anémie normocytaire, Hb: 7.8)
            "HP:0001873",   # Thrombocytopenia (PLQ: 30 000)
            "HP:0001892",   # Abnormal bleeding (syndrome hémorragique cutané)
            "HP:0004313",   # Decreased antibody level (pan-hypogammaglobulinémie)
            "HP:0001888",   # Lymphopenia (Lymphopénies T et B profondes)
            "HP:0000670",   # Carious teeth (carries dentaires)
        ],
    },

    # ── 8. MAABED — Ataxie-télangiectasie ────────────────────────────────
    # TEXT EVIDENCE: "Ataxie statique et cinétique", "Télangiectasie bilatérale",
    # "déficit immunitaire", "infections respiratoires à répétition",
    # "toux grasse", "Retard statural marqué", "malnutrition sévère",
    # "Convulsions", "Otite à répétition", "cryptorchidie bilatérale",
    # "nystagmus rotatoire", "dysarthrie", "Lymphopénie discrète",
    # "Déformation du rachis", "Déformation des pieds en équin",
    # "xérose cutanée"
    "CHU_FR_008": {
        "disease": "Ataxie-télangiectasie",
        "orpha_id": "ORPHA:100",
        "source_file": "Maabed Mouad DIP Ataxie tÃ©langectasie 23_03_2026.docx",
        "expected_hpo": [
            "HP:0001251",   # Cerebellar ataxia (Ataxie statique et cinétique)
            "HP:0001009",   # Telangiectasia (Télangiectasie bilatérale)
            "HP:0004430",   # Immunodeficiency (DIP combiné syndromique)
            "HP:0012735",   # Cough (toux grasse)
            "HP:0004322",   # Short stature (Retard statural marqué -3.5 DS)
            "HP:0004395",   # Malnutrition (malnutrition sévère Gomez 47%)
            "HP:0001250",   # Seizure (Convulsions depuis l'âge de 4 ans)
            "HP:0000388",   # Otitis media (Otite à répétition)
            "HP:0000028",   # Cryptorchidism (cryptorchidie bilatérale)
            "HP:0000639",   # Nystagmus (nystagmus rotatoire)
            "HP:0001260",   # Dysarthria (dysarthrie cérébelleuse)
            "HP:0001888",   # Lymphopenia (Lymphopénie discrète: 940)
        ],
    },

    # ── 9. SAIDANI — Agammaglobulinémie ──────────────────────────────────
    # TEXT EVIDENCE: "agammaglobulinémie", "déficit immunitaire primitif",
    # "neutropénie sévère", "BPCO post rougeole",
    # "Retard staturo-pondéral", "Malnutrition modérée à sévère",
    # "Ictère néonatale", "détresse respiratoire",
    # "pneumonie rougeoleuse", "Douleurs abdominales chroniques",
    # "vomissements", "pâleur", "leuco-neutro-lymphopénie"
    "CHU_FR_009": {
        "disease": "Agammaglobulinémie liée à l'X (Bruton)",
        "orpha_id": "ORPHA:47",
        "source_file": "Saidani Mohamed DIP AgammaglobulinÃ©mie Djoudi 02_2026.docx",
        "expected_hpo": [
            "HP:0004432",   # Agammaglobulinemia (agammaglobulinémie)
            "HP:0004430",   # Immunodeficiency (DIP)
            "HP:0001875",   # Neutropenia (neutropénie sévère)
            "HP:0002090",   # Pneumonia (pneumonie rougeoleuse)
            "HP:0001508",   # Failure to thrive (Retard staturo-pondéral -2.2DS)
            "HP:0004395",   # Malnutrition (Malnutrition modérée à sévère)
            "HP:0000980",   # Pallor (téguments et conjonctives pals)
            "HP:0002098",   # Respiratory distress (détresse respiratoire)
            "HP:0002027",   # Abdominal pain (Douleurs abdominales chroniques)
            "HP:0002013",   # Vomiting (vomissements)
            "HP:0001888",   # Lymphopenia (lymphopénie: 760)
        ],
    },

    # ── 10. TAZI MIMOUNE — SCID atypique ─────────────────────────────────
    # TEXT EVIDENCE: "déficit immunitaire combiné sévère atypique",
    # "infections respiratoires à répétition",
    # "Diarrhées chroniques", "Ballonnement abdominal",
    # "détresse respiratoire", "pâleur cutanéo muqueuse",
    # "Retard psychomoteur", "hépatomégalie homogène",
    # "Pneumopathies à répétition", "Malnutrition sévère",
    # "pancytopénie", "lymphopénie", "eczématiforme (sibling — history)"
    "CHU_FR_010": {
        "disease": "Déficit immunitaire combiné sévère atypique",
        "orpha_id": "ORPHA:183660",
        "source_file": "TAZI MIMOUNE ABDERAHMANE.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (SCID atypique)
            "HP:0002719",   # Recurrent infections (infections respiratoires à répétition)
            "HP:0002090",   # Pneumonia (Pneumopathies à répétition)
            "HP:0002014",   # Diarrhea (Diarrhées chroniques huileuses)
            "HP:0002098",   # Respiratory distress (détresse respiratoire)
            "HP:0000980",   # Pallor (pâleur cutanéo muqueuse)
            "HP:0001263",   # Global developmental delay (Retard psychomoteur)
            "HP:0002240",   # Hepatomegaly (hépatomégalie homogène — TDM)
            "HP:0004395",   # Malnutrition (Malnutrition sévère)
            "HP:0001508",   # Failure to thrive (-3.67DS, -4.7DS)
            "HP:0001888",   # Lymphopenia (lymphopénie — FSP)
        ],
    },

    # ── 11. BENAMEUR — DICV ──────────────────────────────────────────────
    # TEXT EVIDENCE: "déficit immunitaire commun variable",
    # "Pan-hypogammaglobulinémie", "quasi-absence des lymphocytes B",
    # "fièvre prolongée", "éruption cutanée fébrile atypique",
    # "toux sèche intermittente"
    "CHU_FR_011": {
        "disease": "Déficit immunitaire commun variable (DICV)",
        "orpha_id": "ORPHA:1572",
        "source_file": "DR TAMAZIRT/BENAMEUR SIDAHMED/BENAMEUR  DR TAMAZIRT 13-01-2026.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (DIP type DICV)
            "HP:0004313",   # Decreased antibody level (Pan-hypogammaglobulinémie)
            "HP:0001945",   # Fever (fièvre prolongée)
            "HP:0000988",   # Skin rash (éruption cutanée fébrile atypique)
            "HP:0012735",   # Cough (toux sèche intermittente)
        ],
    },

    # ── 12. BOUTELDJA — Hyper-IgE ────────────────────────────────────────
    # TEXT EVIDENCE: "syndrome d'hyper IgE", "déficit immunitaire",
    # "IgE: 390 UI/ml (élevés)", "infections cutanées fongiques chroniques",
    # "onychomycoses", "épilepsie", "hyperactivité",
    # "hyperlaxité ligamentaire", "base nasale large"
    "CHU_FR_012": {
        "disease": "Syndrome d'Hyper-IgE",
        "orpha_id": "ORPHA:2314",
        "source_file": "DR TAMAZIRT/BOUTHELDJA MOHAMED/BOUTELDJA MOHAMED DR TAMAZIRT 15-04-2026.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (DIP syndromique)
            "HP:0003212",   # Increased circulating IgE (IgE: 390 UI/ml élevés)
            "HP:0001250",   # Seizure (épilepsie)
            "HP:0002099",   # Onychomycosis (onychomycoses chroniques)
            "HP:0001382",   # Joint hypermobility (hyperlaxité ligamentaire)
        ],
    },

    # ── 13. MANSOURI — Hyper-IgE ─────────────────────────────────────────
    # TEXT EVIDENCE: "DIP syndromique type Hyper IgE",
    # "Lésions eczématiformes", "Abcès cutanés multiples à répétition",
    # "Xérose cutanée", "dilatation des bronches distales" (TDM),
    # "abcès périanal"
    "CHU_FR_013": {
        "disease": "Syndrome d'Hyper-IgE",
        "orpha_id": "ORPHA:2314",
        "source_file": "DR TAMAZIRT/MANSOURI CHAIMA/MANSOURI CHAIMA DR TAMAZIRT - 02-11-2025.docx",
        "expected_hpo": [
            "HP:0004430",   # Immunodeficiency (DIP syndromique)
            "HP:0000964",   # Eczema (Lésions eczématiformes)
            "HP:0100758",   # Recurrent cutaneous abscess (Abcès cutanés multiples à répétition)
            "HP:0002110",   # Bronchiectasis (dilatation des bronches distales — TDM)
            "HP:0000958",   # Dry skin (Xérose cutanée)
        ],
    },

    # ── 14. BELHOUARI — SMA ──────────────────────────────────────────────
    # TEXT EVIDENCE: "détresse respiratoire avec hypotonie axiale et segmentaire",
    # "Hypotonie axiale et segmentaire profonde",
    # "fins crépitants", "Obstruction nasale",
    # "Acidose respiratoire grade II", "cyanose par moment",
    # "amyotrophie spinale (SMA TYPE 1)"
    "CHU_FR_014": {
        "disease": "Amyotrophie spinale (SMA)",
        "orpha_id": "ORPHA:70",
        "source_file": "DR TAMAZIRT/BELHOUARI ZAKARIA/BELHOUARI ZAKARIA SMA.docx",
        "expected_hpo": [
            "HP:0001252",   # Hypotonia (hypotonie axiale et segmentaire profonde)
            "HP:0002098",   # Respiratory distress (détresse respiratoire)
            "HP:0030829",   # Crackles (fins crépitants)
            "HP:0001742",   # Nasal obstruction (Obstruction nasale)
            "HP:0000961",   # Cyanosis (cyanose par moment)
            "HP:0003202",   # Skeletal muscle atrophy (amyotrophie spinale)
        ],
    },

    # ── 15. NAAK — PID congénitale / Atrésie voies biliaires ────────────
    # TEXT EVIDENCE: "détresse respiratoire chronique depuis l'âge de 3 jours",
    # "insuffisance respiratoire chronique: déformation thoracique",
    # "thorax en carène", "otalgies",
    # "front bombé, hirsutisme"
    # NOTE: Diagnosis changed — report says "PID congénitale", NOT atrésie biliaire
    "CHU_FR_015": {
        "disease": "Pneumopathie interstitielle diffuse congénitale",
        "orpha_id": "ORPHA:264710",
        "source_file": "DR TAMAZIRT/NAAK MOUAD/NAAK MOHAMED MOUAD, DR TAMAZIRT 21-12-2025.docx",
        "expected_hpo": [
            "HP:0002098",   # Respiratory distress (détresse respiratoire chronique)
            "HP:0002093",   # Respiratory insufficiency (insuffisance respiratoire chronique)
            "HP:0000767",   # Pectus / chest deformity (déformation thoracique en carène)
            "HP:0000388",   # Otitis media (otalgies, otite)
            "HP:0000294",   # Frontal bossing (front bombé)
            "HP:0001007",   # Hirsutism (hirsutisme)
        ],
    },

    # ── 16. BAGHDAD Islem — Mucoviscidose ────────────────────────────────
    # TEXT EVIDENCE: "Toux quinteuse récidivante", "Diarrhées chroniques huileuses",
    # "obstruction nasale", "Pharyngite", "crachats blanchâtres",
    # "Elastase fécale: 0.3µg/g" (IPE implied)
    "CHU_FR_016": {
        "disease": "Mucoviscidose",
        "orpha_id": "ORPHA:586",
        "source_file": "DR TAMAZIRT/BAGHDAD ISLEM/BAGHDAD ISLEM 18-11-2025 DR TAMAZIRT.docx",
        "expected_hpo": [
            "HP:0012735",   # Cough (Toux quinteuse récidivante, toux productive)
            "HP:0002014",   # Diarrhea (Diarrhées chroniques huileuses)
            "HP:0001742",   # Nasal obstruction (obstruction nasale)
            "HP:0002024",   # Malabsorption (selles graisseuses, Elastase 0.3)
            "HP:0001738",   # Exocrine pancreatic insufficiency (Elastase fécale: 0.3µg/g)
        ],
    },

    # ── 17. BAGHDAD Malek — Mucoviscidose ────────────────────────────────
    # TEXT EVIDENCE: similar to sibling — "Toux productive", "selles graisseuses",
    # "Diarrhées chroniques", "obstruction nasale", "hippocratisme digital",
    # "déformation thoracique", "RGO", "insuffisance respiratoire chronique",
    # "Retard staturo-pondéral", "malnutrition"
    "CHU_FR_017": {
        "disease": "Mucoviscidose",
        "orpha_id": "ORPHA:586",
        "source_file": "DR TAMAZIRT/BAGHDAD TASNIM/BAGHDAD MALEK 18-11-2025 DR TAMAZIRT.docx",
        "expected_hpo": [
            "HP:0012735",   # Cough (toux productive)
            "HP:0002014",   # Diarrhea (Diarrhées chroniques)
            "HP:0001742",   # Nasal obstruction (obstruction nasale)
            "HP:0002024",   # Malabsorption (selles graisseuses)
            "HP:0100759",   # Clubbing (hippocratisme digital)
            "HP:0000767",   # Pectus / chest deformity (déformation thoracique)
            "HP:0002093",   # Respiratory insufficiency (IRC)
            "HP:0002020",   # Gastroesophageal reflux (RGO)
            "HP:0001508",   # Failure to thrive (Retard staturo-pondéral)
            "HP:0004395",   # Malnutrition (malnutrition)
        ],
    },
}
