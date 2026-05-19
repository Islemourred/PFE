"""
French Mock Clinical Notes — Extracts from CHU Oran pediatric reports.
These are representative excerpts from real hospital reports (anonymized)
used to validate the French pipeline.

Source: Collaboration CHU Oran — Service Immunologie/Pneumologie Pédiatrique
Period: November 2025 — May 2026
"""

# Note: These are condensed versions of the real reports for pipeline testing.
# PHI has been kept minimal and will be masked by Module 1.

FRENCH_NOTES = {
    "NOTE_FR_001": {
        "pathology": "Mucoviscidose (Cystic Fibrosis)",
        "text": """Compte rendu d'hospitalisation
      L'enfant ABDELLAOUI MOHAMED YANIS âgé de 04 ans et demi originaire et demeurant à Oran, suivi depuis l'âge de 03 mois pour une mucoviscidose à double expression phénotypique respiratoire et digestive, réadmis pour exacerbation modérée à Pseudomonas Aeruginosa.
ANTECEDENTS :
Familiaux :
- Père : 41ans ; BES.
- Mère : 27 ans, BES.
- Consanguinité de 2eme degré.
Personnels :
Grossesse : bien suivie
Accouchement : par VB à terme.
Allaitement maternel jusqu'à 06 mois puis artificiel
Diversification alimentaire : 06 mois.
Vaccination : faite correctement
Pathologique :
Depuis l'âge de 03 mois : encombrement bronchique chronique, toux grasse persistante, infections respiratoires à répétition.
Diarrhée chronique graisseuse avec ballonnement abdominal et retard pondéral.
Diagnostic principal : Mucoviscidose
Date de diagnostic : 2022
Éléments de diagnostic :
Test de la sueur positif :
01er Test 26/09/2011 (Avant-bras Gauche) 82 mg 81 meq/l
02ème Test 29/11/2011 (Avant-bras Droit) 216 mg 93 meq/l
Étude génétique : 31/01/2012 : mutation homozygote p.F508del
Elastase fécale 26/03/2025 : 1,8ug/ insuffisance pancréatique exocrine
Traitement en cours :
- Kinésithérapie respiratoire à domicile biquotidienne
- Nébulisation hypertonique
- Nébulisation par Colistine 2 fois par jour un mois sur 2
- Créon 12000 UI (520UI/Kg)
- Vit K 10 mg/15j, Vit D amp/3 mois, Vit E 1cp/j
HISTOIRE DE LA MALADIE :
Le début des signes remonte 15 jours auparavant par accentuation de la toux devenant gênante, modification des crachats qui sont devenus verdâtres et épais, avec asthénie et diminution de l'appétit d'où son admission.
EXAMEN CLINIQUE À L'ADMISSION : Date : 24/03/2026
Mesures anthropométriques :
Poids : 13,600 kg (-1,79 DS). Taille : 100 cm (-1,43 DS). IMC: 13,6 kg/m2 (-1,4 DS).
État général moyen, fébrile : T : 38,7° C, malnutrition légère.
Examen de la peau : Pâleur cutanée, pas d'ictère, ni syndrome hémorragique.
Examen ORL : rhinite allergique
Examen pleuro pulmonaire : FR : 30 c/min, quintes de Toux grasses, Auscultation, râles ronflants bilatéraux, murmures vésiculaires bien transmis dans les 2 champs pulmonaires. Pas de signes d'insuffisance respiratoire chronique (pas d'hippocratisme digital). SPO2 : 96% sous AA.
Examen cardiovasculaire : FC : 100 bpm, Auscultation : B1B2 audibles, pas de souffle ni BSA.
Examen de l'abdomen: souple, transit conservé, pas d'organomégalie.
BILAN PARACLINIQUE :
NFS : GB : 12500 éléments/ul (PNN : 9200 Lymph : 2800) Hb : 11.2 g/dl Plaquette : 280 000
CRP : 45 mg/L
ECBC : Pseudomonas Aeruginosa sensible à la Colistine et Ciprofloxacine.
""",
    },

    "NOTE_FR_002": {
        "pathology": "Syndrome de Wiskott-Aldrich (DIP)",
        "text": """Compte Rendu de REhospitalisation HDJ
      L'enfant Amroun Abdel Aziz, âgé de 09 ans originaire de Chlef et demeurant à Oran, suivi dans notre service depuis 11/01/2021 pour un déficit immunitaire primitif type syndrome de Wiskott Aldrich, compliqué d'une dilatation des bronches DDB cylindrique et insuffisance respiratoire chronique stade 1. Admis le 12/03/2026 pour sa cure 53 d'immunoglobulines.
Diagnostic principal : DIP type Wiskott Aldrich
Date de diagnostic : 05/2020
Éléments de diagnostic :
Clinique : Eczéma depuis l'âge de 10 jours, thrombopénie avec micro plaquettes, infections respiratoires à répétition.
Paraclinique :
Bilan immunologique : IgG 6,49 g/l, IgA 0,67 g/l, IgM 0,17 g/l, IgE 1290 UI/ml (élevée)
Étude génétique : mutation du gène WASP confirmée.
Traitement en cours :
- Itraconazole 5mg/kg/jour
- Bactrim prophylactique 25mg/kg/jour
- Kinésithérapie respiratoire quotidienne
- Cures d'immunoglobulines mensuelles (0,8g/kg)
Retentissement de la maladie :
Sur le plan nutritionnel : Poids: 24,500 kg (-1 DS), Taille :127 cm (-0,7 DS), IMC: 15,3 (-0,9DS). Malnutrition légère.
Sur le plan respiratoire : DDB cylindrique bilatérale, insuffisance respiratoire chronique stade 1.
Sur le plan cutané : Eczéma modéré contrôlé sous émollients.
EXAMEN CLINIQUE À L'ADMISSION : Date : 12/03/2026
État général conservé, apyrétique : T : 36,5°C.
Examen de la peau : eczéma résiduel aux plis, ecchymoses multiples, pas de pétéchies.
Examen ORL : pas d'ADP cervicales.
Examen pleuro pulmonaire : FR : 20 c/min. Auscultation : râles polymorphes.
Examen cardiovasculaire : FC : 98 bpm, pas de souffle ni BSA.
Examen de l'abdomen : souple, pas d'organomégalie.
NFS : GB : 7400 (PNN : 5700 Lymph : 1200) Hb : 10.6 g/dl Plaquette : 90 000 éléments/ul
CRP : négative
""",
    },

    "NOTE_FR_003": {
        "pathology": "Agammaglobulinémie congénitale (Bruton)",
        "text": """Fiche de Ré hospitalisation :
C'est l'enfant AZZEMMOU MAHDI né le 23/04/2016, âgé actuellement de 9 ans et 7 mois, originaire et demeurant à MOSTAGANEM, issu d'un couple non consanguin, suivi à l'EPH BOUGUIRAT MOSTAGANEM depuis 2022 pour un déficit immunitaire primitif type agammaglobulinémie congénitale, hospitalisé à notre niveau ce jour pour la cure d'immunoglobulines N : 43.
Diagnostic principal : Déficit immunitaire primitif type Agammaglobulinémie congénitale
Diagnostics associés : Aucun
Date de diagnostic : 23/08/2022
Éléments de diagnostic :
Anamnestiques :
- Un frère décédé en 2022 dans un tableau de détresse respiratoire au niveau de la réanimation pédiatrique (IMC sur méningite à l'âge de 6 ans)
- Un oncle maternel décédé à l'âge de 18 mois d'étiologies inconnues.
Clinique :
- Otites purulentes avec arthrite du genou gauche à répétition depuis l'âge de 5 ans.
- Toux grasse chronique depuis l'âge de 5 ans.
Paraclinique :
Bilan du déficit immunitaire : fait le 23/08/2022 :
IgG : 0,33 g/l IgA : 0,26 g/l IgM : 0,181 g/l.
Absence de lymphocytes B.
Le tableau est en faveur d'une Agammaglobulinémie congénitale.
Traitement en cours :
- Itraconazole 1cp/j
- Bactrim 1cp jour par jour
- Kinésithérapie
Retentissement de la maladie :
Sur le plan nutritionnel :
Poids: 28,500 kg (- 0,5 DS). Taille :134 cm (-0,3 DS) IMC: 15,9 (-0,7DS)
Légère malnutrition
EXAMEN CLINIQUE À L'ADMISSION : 25/03/2026
État général conservé, apyrétique : T° 36.7 C, bonne coloration cutanéomuqueuse.
Examen de la peau : Pas de lésion de cuir chevelu. Présence de cicatrices au niveau du genou gauche.
Examen ORL : absence d'otorrhée, absence d'otalgie. Gorge propre, caries dentaires.
Examen pleuro pulmonaire : Toux grasse crachats blanchâtres, pas de déformation thoracique, pas de signe d'insuffisance respiratoire chronique.
FR : 22 cycles/min, SPO2 :99 % sous air ambiant.
Auscultation pulmonaire : râles polymorphes aux 2 champs pulmonaires.
Examen cardiovasculaire : FC : 80 b/min. B1B2 bien audibles, pas de souffle ni BSA.
Examen abdominal : souple, pas d'organomégalie.
""",
    },

    "NOTE_FR_004": {
        "pathology": "SCID atypique (SCID-like)",
        "text": """FICHE D'HOSPITALISATION:
Il s'agit du nourrisson Tazi Mimoun Abderrahmane, âgé de 14 mois originaire et demeurant à Saida, issu d'un couple consanguin de 2ème degré, suivi depuis l'âge de 05 mois pour déficit immunitaire combiné sévère atypique, orienté depuis l'EPH de Saida pour complément de suivi et prise en charge d'un Syndrome infectieux.
ANTÉCÉDENTS :
Familiaux :
Père : 41ans, bon état de santé.
Mère : 33ans, bon état de santé.
Fratrie :
fille décédée en 2016, à l'âge d'un mois dans un tableau eczématiforme généralisé (probablement : greffon contre hôte)
Garçon décédé en 2017 à l'âge de 05 mois dans un tableau de détresse respiratoire, diarrhée et ballonnement abdominal (SCID-LIKE probable)
Consanguinité : oui
Personnels :
Grossesse: bien suivie
Accouchement: à terme par voie haute
Apgar 10/10
Poids de naissance : 3.9kg
Pathologique :
Plusieurs hospitalisations pour broncho-pneumopathies à répétition et diarrhées chroniques
Diagnostic principal : Déficit immunitaire combiné sévère atypique
Date de diagnostic : 04/2025
Éléments de diagnostic :
Clinique :
Infections respiratoires à répétition
Diarrhées chroniques depuis l'âge de 03 mois
Ballonnement abdominal
Paraclinique :
Bilan de déficit immunitaire (21/04/2025): déficit immunitaire combiné sévère atypique
Traitement en cours :
Antibiothérapie cyclique : Bactrim/Augmentin
Nébulisation par pulmicort + asthalin
EXAMEN CLINIQUE À L'ADMISSION :
Poids: 06kg600 (-3.67DS) Taille: 67cm (-4.7DS) Malnutrition sévère
IMC: 14.7 (moins de P3)
État général : moyen, T° 36.7 c, dextro : 1 g/l
Légèrement déshydraté
Examen de la peau :
légère pâleur cutanéo muqueuse,
Lésion de BCGite de cicatrisation,
Pas de cicatrices, ni d'abcès
Examen ORL :
pas de ADP cervicale
Pas de candidose buccale
Examen pleuro pulmonaire :
FR 37 c/mn
Léger tirage sus sternal. SPO2 : 98 % AA
Auscultation pulmonaire: clair aux 2CP
Pas de signes d'insuffisance respiratoire chronique
Examen cardiovasculaire :
FC : 110 b/min.
Auscultation : B1B2 audibles pas de souffles ni BSA
Examen digestif :
abdomen souple ballonné PA:47cm
pas d'organomégalies,
Notion de diarrhée à raison de 06 selles/jour de couleur normale et d'aspect huileux
Sexe de morphotype masculin
NFS : GB: 8200 (PNN: 4100 Lymph: 2800) Hb: 9.8 g/dl Plaquettes: 340000
CRP: 12 mg/L
""",
    },

    "NOTE_FR_005": {
        "pathology": "Déficit en HLA-DR (MHC class II deficiency)",
        "text": """Compte Rendu d'hospitalisation (cure d'immunoglobuline)
Le nourrisson Abdoune Lyne Hasnia, âgée de 2 ans et 2 mois, originaire et demeurant à Saida, issue d'un couple jeune consanguins du 2eme degré, suivie à notre niveau pour la prise en charge d'un déficit immunitaire primitif combiné sévère type HLADR depuis juin 2025, admise ce jour pour la cure d'immunoglobuline N 12.
Diagnostic principal : déficit immunitaire primitif DIP type HLADR
Diagnostics associés : aucun
Date du diagnostic : juin 2025
Éléments de diagnostic :
Clinique :
Infections respiratoires à répétition depuis l'âge de 03 mois
Diarrhées chroniques
Retard staturo-pondéral
Paraclinique :
Bilan immunologique : déficit en molécules HLA de classe II
Déficit profond en lymphocytes T CD4+
Traitement en cours :
Bactrim prophylactique
Cures d'immunoglobulines mensuelles
EXAMEN CLINIQUE À L'ADMISSION :
Poids: 08,500 kg (-2,5 DS) Taille: 79 cm (-2,1 DS)
Malnutrition modérée
État général conservé, apyrétique T : 36.8° C
Examen de la peau : pâleur cutanéo-muqueuse modérée, pas de lésions cutanées
Examen ORL : gorge propre, pas d'ADP
Examen pleuro pulmonaire : FR : 28 c/min, pas de signes de détresse respiratoire
Auscultation : quelques râles bronchiques bilatéraux
SPO2 : 97% sous AA
Examen cardiovasculaire : FC : 120 b/min, B1B2 audibles, pas de souffles
Examen abdominal : souple, transit conservé, pas d'organomégalie
NFS : GB: 6500 (PNN: 3200 Lymph: 1800) Hb: 10.5 g/dl Plaquettes: 250000
CRP : négative
""",
    },
}


def get_french_notes() -> dict:
    """Return all French clinical test notes."""
    return FRENCH_NOTES


def get_french_note_ids() -> list:
    """Return all French note IDs."""
    return list(FRENCH_NOTES.keys())
