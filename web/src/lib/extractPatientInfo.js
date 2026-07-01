/**
 * Extract patient info from French medical report text.
 * Port of the Python extract_patient_info logic.
 */
export function extractPatientInfo(text) {
  const info = {};

  // Dossier number
  const dossierNum = text.match(/(?:Dossier\s+)?N[°0o]\s*(?:Dossier)?\s*[:：]\s*(\d{3,6})/i);
  if (dossierNum) info.dossier_number = dossierNum[1].trim();

  // Name + Age
  const nameAge = text.match(
    /(?:L['\u2019]enfant|Le\s+nourrisson|Le\s+patient|La\s+patiente|L['\u2019]adolescent)\s+([A-Z\u00C0-\u0178a-z\u00e0-\u00ff\s\-]+?)(?:,|\s+)\s*(?:\u00e2g\u00e9e?|ag\u00e9e?|age)\s+(?:de\s+)?(\d+\s*(?:ans?|mois|jours?)(?:\s+et\s+(?:demi|\d+\s*mois))?)/i
  );
  if (nameAge) {
    info.full_name = nameAge[1].trim().replace(/\b\w/g, c => c.toUpperCase());
    info.age = nameAge[2].trim();
  }

  // Gender
  if (/\bfille\b|f\u00e9minin|La\s+patiente/i.test(text)) {
    info.gender = "F";
  } else if (/\bgar\u00e7on\b|masculin|Le\s+patient|Sexe\s+masculin/i.test(text)) {
    info.gender = "M";
  }

  // Origin
  const origin = text.match(
    /originaire\s+(?:et\s+demeurant\s+)?(?:de|d['\u2019]|\u00e0)\s+([A-Z\u00C0-\u0178a-z\u00e0-\u00ff\s\-]+?)(?:[,.]|\s+(?:suivi|issue|adress))/i
  );
  if (origin) {
    info.origin = origin[1].trim().replace(/\b\w/g, c => c.toUpperCase());
    info.residence = info.origin;
  }

  // Parents
  const father = text.match(/P\u00e8re\s*:\s*(\d+\s*ans?[^.\n]*)/i);
  if (father) info.parent_father = father[1].trim();

  const mother = text.match(/M\u00e8re\s*:\s*(\d+\s*ans?[^.\n]*)/i);
  if (mother) info.parent_mother = mother[1].trim();

  // Consanguinity
  const consang = text.match(/[Cc]onsanguinit[\u00e9e]\s+(?:du?\s+)?([^.\n]+)/);
  if (consang) info.consanguinity = consang[1].trim();

  // Principal diagnosis
  const diag = text.match(/[Dd]iagnostic\s+principal\s*[:]?\s*([^\n.]+)/);
  if (diag) info.principal_diagnosis = diag[1].trim();

  // Associated diagnoses
  const assoc = text.match(/[Dd]iagnostics?\s+associ[\u00e9e]s?\s*[:]?\s*([^\n]+)/);
  if (assoc) {
    const val = assoc[1].trim();
    if (val.toLowerCase() !== "aucun") info.associated_diagnoses = val;
  }

  // Date of diagnosis
  const diagDate = text.match(/[Dd]ate\s+d[ue]\s+diagnostic\s*[:]?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})/);
  if (diagDate) {
    try {
      const d = diagDate[1].replace(/\//g, "-").split("-");
      info.date_of_diagnosis = `${d[2]}-${d[1].padStart(2, "0")}-${d[0].padStart(2, "0")}`;
    } catch { /* ignore */ }
  }

  // Age at diagnosis
  const ageDiag = text.match(/[Aa]ge\s+(?:au|de)\s+diagnostic\s*[:]?\s*([^\n.]+)/);
  if (ageDiag) info.age_at_diagnosis = ageDiag[1].trim();

  // Treating doctor
  const doctor = text.match(/\b(?:Dr|DR)\s+([A-Z\u00C0-\u0178][a-z\u00e0-\u00ff]+)/);
  if (doctor) info.treating_doctor = doctor[1].trim().replace(/\b\w/g, c => c.toUpperCase());

  return info;
}

/**
 * Extract info from filename
 */
export function extractFromFilename(filename) {
  const name = filename.replace(".docx", "").replace(/_/g, " ");
  const info = {};

  const docMatch = name.match(/(?:DR|Dr|dr)[\s._]+([A-Za-z\u00C0-\u00ff]+)/i);
  if (docMatch) info.treating_doctor = docMatch[1].trim().replace(/\b\w/g, c => c.toUpperCase());

  const pathologies = [
    "Mucoviscidose", "Wiskott-Aldrich", "Wiskott Aldrich",
    "Agammaglobulinémie", "SCID", "SKID",
    "DIP", "Déficit", "Deficit", "SMA", "HIES", "HLA-DR", "HLA DR"
  ];
  for (const p of pathologies) {
    if (name.toLowerCase().includes(p.toLowerCase())) {
      info.principal_diagnosis = p;
      break;
    }
  }

  // Try to extract patient name from filename
  let patientName = name;
  const drPos = patientName.search(/\b(?:DR|Dr|dr)\b/);
  if (drPos > 0) patientName = patientName.substring(0, drPos).trim();
  for (const p of pathologies) {
    patientName = patientName.replace(new RegExp(p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), '').trim();
  }
  patientName = patientName.replace(/\d{1,2}[-/]\d{1,2}[-/]\d{4}/g, '').trim();
  patientName = patientName.replace(/\s+/g, ' ').trim().replace(/^[-_,.\s]+|[-_,.\s]+$/g, '');
  patientName = patientName.replace(/^(RM|CERTIFICAT MEDICAL|Novembre|Décembre|Janvier|Février|Mars|Avril|Mai|Juin)\s*/i, '').trim();
  patientName = patientName.replace(/\s*(Novembre|Décembre|Janvier|Février|Mars|Avril|Mai|Juin|recu|Copie|HDJ|reçu)\s*\d*\s*$/i, '').trim();
  patientName = patientName.replace(/^[-_,.\s]+|[-_,.\s]+$/g, '');

  if (patientName.length >= 2) {
    info.full_name = patientName.replace(/\b\w/g, c => c.toUpperCase());
  }

  return info;
}
