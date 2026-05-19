"""
Raw Clinical Notes — realistic doctor-written notes with PHI, abbreviations, messy formatting.
These look like actual EMR/EHR notes, not clean synthetic data.
"""

raw_notes = [
    # ── NOTE 1: Ehlers-Danlos Syndrome ────────────────────────────────────
    {
        "id": "NOTE_001",
        "text": """
Patient: Sarah Mitchell
DOB: 05/14/2001   MRN: 7834291   Sex: F

Date: 04/07/2026
Attending: Dr. Rebecca Thornton, Genetics

CC: joint pain, skin tears easily

HPI: 25yo F referred by Dr. Kaplan (rheumatology) for eval of chronic joint
     problems. Pt reports hx of bilateral shoulder dislocations x4 since age 16,
     R knee subluxation x2, chronic low back pain. Skin is "paper thin" per pt,
     bruises easily with minimal trauma. Mother has similar sx - never diagnosed.
     Beighton score 8/9 today.

PMH: bilateral shoulder instability, chronic pain syndrome, GERD
Meds: naproxen 500mg BID, omeprazole 20mg daily
Allergies: NKDA
FHx: mother w/ joint hypermobility, easy bruising. MGM w/ "loose joints"

PE: skin hyperextensible at forearms (~4cm). Molluscoid pseudotumors at elbows.
    Joint hypermobility: thumbs to forearms bilat, knees hyperextend >10deg,
    elbows hyperextend >10deg, palms flat on floor. Multiple ecchymoses on shins.

A/P: clinical picture c/w Ehlers-Danlos Syndrome, hypermobility type (hEDS).
     1. Send COL5A1, COL5A2 genetic panel - Quest
     2. PT referral for joint stabilization program
     3. Continue naproxen, add duloxetine 30mg for chronic pain
     4. Avoid contact sports, wt lifting
     5. Refer ophtho for lens subluxation screening
     6. f/u 6 wks w/ genetic results
"""
    },

    # ── NOTE 2: Cystic Fibrosis ──────────────────────────────────────────
    {
        "id": "NOTE_002",
        "text": """
Pt: Ahmed R. Benali
DOB: 03/10/2018   MRN: 5521908   Sex: M
Visit Date: 04/10/2026
Provider: Dr. Lisa Chang, Pediatric Pulmonology

CC: persistent cough, failure to gain weight

HPI: 8yo M w/ known CF (dx age 2) presents for quarterly f/u. Mom reports
     increased cough x3 wks, productive of thick yellow-green sputum. Poor
     appetite, lost 1.2kg since last visit. No hemoptysis. No fever. Currently
     on pancreatic enzyme replacement (Creon 12k units w/ meals).
     Last PFT 3 mo ago: FEV1 72% predicted.

     Previous cultures: Pseudomonas aeruginosa (mucoid strain), MRSA neg.

PMH: CF (homozygous F508del), meconium ileus s/p surgical repair (neonatal),
     pancreatic insufficiency, recurrent pneumonia x5 episodes
Meds: Creon 12k TID w/ meals, inhaled tobramycin (alternating months),
      dornase alfa daily, azithromycin 250mg MWF, multivitamin w/ ADEK
Allergies: PCN - rash

Labs today:
  CBC: WBC 14.2, Hgb 11.8, Plt 342
  CMP: Na 136, K 4.1, Cl 98, BUN 12, Cr 0.4, Gluc 92
  Sweat Cl: 82 mmol/L (prior)
  Sputum cx: pending

PFT: FEV1 65% predicted (down from 72%), FVC 78%

A/P:
  1. FEV1 decline - start CFTR modulator elexacaftor/tezacaftor/ivacaftor
     (Trikafta) given F508del genotype. Check LFTs in 1 month.
  2. Increased sputum - add hypertonic saline nebs BID
  3. Weight loss - increase Creon to 18k w/ meals, nutrition consult
  4. Continue tobramycin cycle. Await sputum cx.
  5. Flu + COVID vax update
  6. f/u 4 wks
"""
    },

    # ── NOTE 3: Huntington Disease ───────────────────────────────────────
    {
        "id": "NOTE_003",
        "text": """
Patient Name: Maria Vasquez
DOB: 07/22/1984   MRN: 3349015   Sex: F
Date of Service: 03/28/2026
Physician: Dr. James O'Brien, Neurology

CC: involuntary movements, personality changes

HPI: 42yo F brought by husband who reports 6mo progressive involuntary
     movements of hands and face. Pt has become increasingly irritable, has
     had 2 episodes of explosive anger (uncharacteristic per husband).
     Difficulty w/ fine motor tasks - dropping things, can't button shirts.
     Depression worsening despite sertraline 100mg. Father dx'ed w/ HD at
     age 45, died at 58. Paternal uncle also affected.

     Pt is aware of family hx but has avoided testing until now due to fear.

PMH: depression (3 yrs), migraine w/ aura, anxiety
Meds: sertraline 100mg daily, sumatriptan 50mg PRN
Allergies: Codeine - nausea

Neuro Exam:
  - Mental status: alert, oriented x3. Flat affect. MMSE 24/30
    (lost points: delayed recall 1/3, serial 7s, copy pentagon)
  - Cranial nerves: intact. Impaired saccadic eye movements.
  - Motor: involuntary choreiform movements bilateral UE > LE.
    Difficulty maintaining grip. Tone mildly increased.
  - Gait: wide-based, mildly ataxic. Impaired tandem walk.
  - Reflexes: 3+ throughout, no clonus

MRI brain: mild caudate atrophy bilaterally

A/P: clinical presentation + FHx highly c/w Huntington Disease
  1. Order HTT gene - CAG repeat analysis (Athena Diagnostics)
  2. Genetic counseling referral - discuss implications for children
  3. Start tetrabenazine 12.5mg BID for chorea, titrate as tolerated
  4. Increase sertraline to 150mg
  5. OT referral for adaptive strategies
  6. Driving safety evaluation
  7. Discuss advance directives at next visit
  8. f/u 3 wks w/ genetic results
"""
    },

    # ── NOTE 4: Sickle Cell Disease ──────────────────────────────────────
    {
        "id": "NOTE_004",
        "text": """
Pt: Elijah Thompson
DOB: 06/01/2023   MRN: 8891204   Sex: M
Visit: 04/12/2026 - ED presentation
Provider: Dr. Priya Sharma, Pediatric Hematology (on-call)

CC: bilateral hand swelling and pain x 12 hrs

HPI: 3yo AA male brought to ED by mother for acute onset bilateral hand
     swelling and severe pain (dactylitis). Pt inconsolable, refusing to
     use hands. 4th pain crisis in past 12 months. Temp 100.4F at home.
     Last crisis 6 wks ago - managed as outpatient w/ oral morphine.
     No URI sx, no cough, no abd pain. On folic acid only - parents
     declined hydroxyurea previously.

     Both parents confirmed sickle cell trait (HbAS).

PMH: SCD (HbSS) - dx newborn screen, dactylitis x3, 1 splenic sequestration
     (age 18mo), received Prevnar + Menactra, on penicillin prophylaxis until
     stopped by parents 4mo ago
Meds: folic acid 1mg daily (poor compliance per mom)
Allergies: NKDA

Vitals: T 101.2F, HR 142, RR 28, BP 88/52, SpO2 95% RA

Labs:
  CBC: WBC 18.4, Hgb 6.8 (baseline 7.5), Hct 20.1, Plt 425, Retic 12.4%
  CMP: BUN 8, Cr 0.3, LDH 892 (H), total bili 4.2 (H), AST 48
  Blood cx: x2 sent
  Type & screen: done

Peripheral smear: sickle cells, target cells, Howell-Jolly bodies

A/P: SCD (HbSS) w/ VOC + dactylitis + fever - concern for sepsis
  1. IV NS bolus 20ml/kg then D5 1/2NS at 1.5x maintenance
  2. IV morphine 0.1mg/kg q3h PRN, start ketorolac 0.5mg/kg q6h
  3. Ceftriaxone 75mg/kg IV (max 2g) empiric - pending cultures
  4. Transfuse pRBC 10ml/kg - Hgb below baseline w/ acute symptoms
  5. Restart penicillin V prophylaxis - counsel parents re: infection risk
  6. Strongly recommend hydroxyurea initiation - meeting w/ parents tomorrow
  7. Admit to pediatric floor, heme attending to assume care AM
"""
    },

    # ── NOTE 5: CONTRADICTION - Male w/ female conditions ────────────────
    {
        "id": "NOTE_005",
        "text": """
Patient: Robert J. Kowalski
DOB: 02/20/1971   MRN: 2240198   Sex: M
Date: 04/01/2026
Provider: Dr. Angela Martinez, General Medicine

CC: pelvic pain x 5 days

HPI: 55yo M presents w/ 5 days of progressive lower abd/pelvic pain,
     R sided, sharp, 7/10, worse w/ movement. Nausea without vomiting.
     Denies dysuria, hematuria, or testicular pain. No prior abd surgery.

Imaging: pelvic US reveals 4.2cm ruptured ovarian cyst w/ free fluid
         in cul-de-sac. Endometrial stripe 8mm.

Labs: WBC 11.1, Hgb 14.2, beta-HCG negative

A/P:
  1. Ruptured ovarian cyst - GYN consult for management
  2. Chronic endometriosis - continue expectant management
  3. Pain control: ketorolac 30mg IV, then ibuprofen 600mg q6h
  4. f/u GYN 1 wk
"""
    },

    # ── NOTE 6: CONTRADICTION - Contradictory lab values ─────────────────
    {
        "id": "NOTE_006",
        "text": """
Pt: Nadia Bouzid
DOB: 04/15/1988   MRN: 6673421   Sex: F
Date: 04/05/2026
Provider: Dr. Hassan El-Amin, Endocrinology

CC: dizziness, confusion

HPI: 38yo F w/ poorly controlled DM2 presents w/ episodic dizziness and
     confusion x 2 wks. Also reports headaches and visual changes.

Labs:
  - fasting glucose: 42 mg/dL (critically low - symptomatic hypoglycemia)
  - HbA1c: 11.2% (indicates chronic severe hyperglycemia)
  - simultaneous C-peptide: 0.8 ng/mL (low)

Vitals: BP 182/108 sitting, BP 78/50 standing (orthostatic hypotension
        with documented hypertension)

Meds: metformin 1000mg BID, glipizide 10mg BID, insulin glargine 40 units QHS

A/P:
  1. Hypoglycemia - likely glipizide/insulin overlap. Hold glipizide.
  2. Chronic hyperglycemia per HbA1c despite hypoglycemic episodes -
     consider glycemic variability, brittle diabetes workup
  3. Hypertension w/ orthostatic hypotension - r/o autonomic neuropathy.
     Start midodrine 5mg TID for orthostasis. Continue lisinopril.
  4. CGM placement for glucose patterns
  5. Endocrine f/u 2 wks
"""
    },

    # ── NOTE 7: CONTRADICTION - Temporal impossibility ───────────────────
    {
        "id": "NOTE_007",
        "text": """
Patient: Lucas Dubois
DOB: 08/30/2021   MRN: 9917845   Sex: M
Date: 04/06/2026
Provider: Dr. Catherine Park, Pediatric Cardiology

CC: follow-up VSD repair

HPI: 5yo M s/p VSD repair in March 2018 at Children's National.
     Procedure performed by Dr. Richardson via median sternotomy,
     primary patch closure. Post-op course uncomplicated per records.

     Mom reports intermittent palpitations x 2 months, especially during
     activity. No syncope, no chest pain, no exercise intolerance. Active,
     playing soccer.

     ***NOTE: patient born 08/30/2021 - surgery date 2018 predates birth***

Vitals: HR 92, BP 95/62, SpO2 99% RA
Echo today: normal biventricular function, LVEF 62%, no residual VSD,
            no valvular regurgitation

EKG: NSR, rate 90, no arrhythmia, normal QTc

A/P:
  1. S/p VSD repair - echo satisfactory, no residual defect
  2. Palpitations - likely benign given normal EKG/echo.
     Order 48hr Holter monitor for reassurance
  3. Clear for sports participation
  4. f/u 1 yr or sooner if palpitations worsen
"""
    },

    # ── NOTE 8: CONTRADICTION - Drug conflicts ───────────────────────────
    {
        "id": "NOTE_008",
        "text": """
Pt: Dorothy Chen-Williams
DOB: 09/12/1961   MRN: 3318760   Sex: F
Date: 04/08/2026
Provider: Dr. Michael Santos, Internal Medicine / Hematology

CC: easy bruising, nosebleeds x 3 wks

HPI: 65yo F w/ hemophilia A (mild, factor VIII 12%) presents w/ worsening
     bruising and 2 episodes of spontaneous epistaxis (lasting 20-30 min each).
     Pt was started on warfarin 5mg daily 2 months ago by cardiology for new
     AFib (CHA2DS2-VASc = 4). Also taking aspirin 81mg daily for CV prophylaxis
     per PCP. Pt did not inform cardiologist of hemophilia diagnosis.

PMH: hemophilia A (mild), AFib (new dx 2mo ago), HTN, osteoarthritis,
     h/o GI bleed 2019
Meds: warfarin 5mg daily, aspirin 81mg daily, metoprolol 50mg BID,
      lisinopril 20mg daily, acetaminophen 650mg PRN
Allergies: sulfa drugs - hives

Labs:
  CBC: WBC 7.2, Hgb 10.8 (baseline 12.4), Plt 42,000 (L)
  Coags: PT 28.4, INR 3.8 (supratherapeutic), aPTT 52
  Factor VIII: 11%
  Fibrinogen: 220

A/P: Hemophilia A + supratherapeutic anticoagulation = HIGH BLEED RISK
  1. HOLD warfarin immediately. Vitamin K 2.5mg PO x1.
  2. STOP aspirin - CONTRAINDICATED with hemophilia
  3. Thrombocytopenia workup: peripheral smear, retic, haptoglobin.
     R/o HIT (heparin-induced) vs drug-induced (warfarin) vs ITP.
  4. Once INR normalized: discuss DOAC vs warfarin w/ closer monitoring
     for AFib. Consult hematology for factor replacement protocol.
  5. GI consult given Hgb drop + h/o GI bleed
  6. Admit for observation. Bleeding precautions.
"""
    },

    # ── NOTE 9: Edge Case - Negation + MIMIC formatting ──────────────────
    {
        "id": "NOTE_009",
        "text": """
Pt: [**Known lastname 4821**], [**Known firstname 1923**]
MRN: [**Clip Number (Identifier) 4822**]
DOB: [**2014-4-20**]   Age: 12   Sex: M
Admission Date: [**2026-4-14**]
Attending: [**First Name8 (NamePattern2) 201**]

Transfer from [**Hospital1 112**] for genetics evaluation.

=================================================================
HISTORY OF PRESENT ILLNESS:
=================================================================
12yo male transferred for eval of suspected connective tissue dz.

The patient has NO joint pain and NO skin rash. He DENIES any
breathing difficulty, chest pain, or palpitations. No visual
problems reported. ROS otherwise negative x14 systems.

However, genetic workup at OSH revealed a pathogenic variant in
FBN1 gene (c.4082G>A, p.Cys1361Tyr) - classified pathogenic.

PE remarkable for: tall stature (>97th %ile for age), arm span
exceeds height by 8cm, positive wrist sign, positive thumb sign,
arachnodactyly, mild pectus excavatum. NO lens subluxation on
slit lamp exam. NO murmur.

Echo: aortic root 2.1cm (z-score +1.8) - upper normal range.

=================================================================
ASSESSMENT AND PLAN:
=================================================================
1. Marfan Syndrome confirmed genetically (FBN1 pathogenic variant)
   - Will be followed with serial echo q6mo
   - Aortic root monitoring protocol initiated
2. NO aortic root dilation currently - reassuring
3. Ophthalmology: NO lens subluxation - continue annual exams
4. Lifestyle: avoid contact sports, isometric exercises, competitive athletics
5. Beta-blocker NOT started at this time given normal aortic dimensions
6. Genetic counseling for family - parents to be tested
7. D/C to home, f/u genetics clinic 6 months
"""
    },

    # ── NOTE 10: Edge Case - Neonate ─────────────────────────────────────
    {
        "id": "NOTE_010",
        "text": """
Patient: Baby Boy Al-Rashid
DOB: 04/10/2026   MRN: 1100483   Sex: M   Age: 5 days
Date: 04/15/2026
NICU Attending: Dr. Yuki Tanaka, Neonatology / Immunology

CC: abnormal newborn screen

HPI: 5 day old male born at 39+2 wks via NSVD to 28yo G2P2 mother.
     Birth weight 3.2kg, APGARs 8/9. Newborn screen flagged for TREC
     absent (T-cell receptor excision circles = 0). Parents are first
     cousins (consanguineous). Older sibling (sister, 3yo) is healthy.

     Infant currently feeding well, no respiratory distress, no rash,
     no diarrhea. Afebrile.

PE: well-appearing neonate, no dysmorphic features.
    HEENT: no thrush. Heart: RRR, no murmur. Lungs: CTA bilat.
    Skin: no rash, no lesions. Umbilicus clean.

CXR: ABSENT thymic shadow - highly suspicious for T-cell deficiency

Labs:
  CBC w/ diff: WBC 4.2, ALC 180/mcL (CRITICALLY LOW - normal >2500)
    Lymphocyte subsets:
      CD3+ T cells: 12/mcL (normal >2500)
      CD4+: 8/mcL
      CD8+: 4/mcL
      CD19+ B cells: 890/mcL (normal)
      CD16/56+ NK cells: 340/mcL (normal)
  IgG: 680 (maternal), IgA: <5, IgM: <5

  Flow cytometry: T-B+NK+ phenotype

A/P: Severe Combined Immunodeficiency (SCID) - T-B+NK+ phenotype
     Most likely X-linked (IL2RG) vs JAK3 deficiency given phenotype

  1. STRICT protective isolation - positive pressure room
  2. IVIG 400mg/kg loading dose, then q3-4wks
  3. PCP prophylaxis: TMP-SMX 5mg/kg/day divided BID
  4. CMV-negative, irradiated, leukocyte-reduced blood products ONLY
  5. NO live vaccines (BCG, rotavirus) - notify family
  6. Genetic testing: IL2RG gene sequencing STAT, JAK3 if negative
  7. HLA typing: patient + parents + sibling for potential HSCT donor
  8. Urgent referral to transplant center - Dr. Buckley at Duke
  9. Social work: family support, discuss prognosis and HSCT timeline
  10. Mother to pump/provide breast milk (beneficial IgA)
"""
    },
]
