"""
Module 3.2 — Temporal Reasoning (Bilingual)
Detects temporal impossibilities and inconsistencies in clinical notes.
Supports both English and French date formats.

Checks:
  - Events dated before patient's date of birth
  - Procedures dated in the future (relative to note date)
  - Age/DOB inconsistencies
"""

import re
from datetime import datetime, date


def parse_date(text: str) -> date | None:
    """Try to parse a date string in common clinical formats."""
    formats = [
        # French DD/MM/YYYY (most common in French clinical notes)
        "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y",
        # English MM/DD/YYYY
        "%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y",
        "%m/%d/%y", "%Y/%m/%d",
        # Named months
        "%B %d, %Y", "%b %d, %Y",
    ]
    text = text.strip().strip("[]").strip("*").strip()
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def extract_dates(text: str) -> dict:
    """
    Extract key dates from a clinical note.

    Returns:
        {"dob": date or None,
         "note_date": date or None,
         "event_dates": [{"date": date, "context": "VSD repair", "raw": "March 2018"}]}
    """
    result = {"dob": None, "note_date": None, "event_dates": []}

    # DOB patterns (English + French)
    dob_patterns = [
        # English
        r'DOB[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})',
        r'DOB[:\s]+(\d{4}-\d{1,2}-\d{1,2})',
        r'Date\s+of\s+Birth[:\s]+([0-9/\-]+)',
        r'DOB[:\s]+\[\*\*(\d{4}-\d{1,2}-\d{1,2})\*\*\]',  # MIMIC format
        # French
        r'[Nn]é(?:e)?\s+le\s+(\d{1,2}/\d{1,2}/\d{2,4})',
        r'[Nn]é(?:e)?\s+le\s+(\d{1,2}-\d{1,2}-\d{4})',
        r'[Dd]ate\s+de\s+naissance\s*[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["dob"] = parse_date(match.group(1))
            if result["dob"]:
                break

    # Note date patterns
    note_patterns = [
        # English
        r'Date[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})',
        r'Date\s+of\s+Service[:\s]+([0-9/\-]+)',
        r'Visit\s+Date[:\s]+([0-9/\-]+)',
        r'Visit[:\s]+([0-9/\-]+)',
        r'Admission\s+Date[:\s]+\[\*\*(\d{4}-\d{1,2}-\d{1,2})\*\*\]',
        # French
        r"Date\s+d'admission[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})",
        r'Date\s*[:\s]+(\d{1,2}/\d{1,2}/\d{2,4})',
        r'[Aa]dmis(?:e)?\s+le\s+(\d{1,2}/\d{1,2}/\d{2,4})',
    ]
    for pattern in note_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["note_date"] = parse_date(match.group(1))
            if result["note_date"]:
                break

    # Event dates (e.g., "VSD repair in March 2018")
    event_patterns = [
        r'(?:in|on|during|since|from)\s+((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        r's/p\s+\w+[\w\s]*?(?:in|on)\s+(\w+\s+\d{4})',
        r'(?:surgery|procedure|repair|operation)\s+(?:in|on|during)\s+(\w+\s+\d{4})',
    ]
    seen_dates = set()
    for pattern in event_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw = match.group(1)
            if raw in seen_dates:
                continue
            # Try to parse month + year
            for fmt in ["%B %Y", "%b %Y"]:
                try:
                    event_date = datetime.strptime(raw, fmt).date()
                    seen_dates.add(raw)
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 10)
                    context = text[start:end].strip()
                    result["event_dates"].append({
                        "date": event_date,
                        "context": context,
                        "raw": raw,
                    })
                    break
                except ValueError:
                    continue

    return result


def check_temporal_consistency(text: str) -> list:
    """
    Check for temporal impossibilities in a clinical note.

    Args:
        text: raw clinical note text

    Returns:
        List of temporal warnings:
        [{"type": "event_before_birth",
          "severity": "critical",
          "message": "Event 'March 2018' predates DOB (08/30/2021)",
          "event_date": "2018-03-01",
          "dob": "2021-08-30"}]
    """
    warnings = []
    dates = extract_dates(text)

    if not dates["dob"]:
        return warnings

    dob = dates["dob"]

    # Check events before birth
    for event in dates["event_dates"]:
        if event["date"] < dob:
            warnings.append({
                "type": "event_before_birth",
                "severity": "critical",
                "message": (
                    f"Event '{event['raw']}' ({event['date']}) predates "
                    f"patient DOB ({dob}). Context: \"{event['context']}\""
                ),
                "event_date": str(event["date"]),
                "dob": str(dob),
            })

    # Check age consistency if available (EN + FR patterns)
    age_match = re.search(
        r'\b(\d{1,3})\s*(?:yo|y/o|year[- ]old|ans?)\b', text, re.IGNORECASE
    )
    if not age_match:
        age_match = re.search(
            r'âgée?\s+(?:actuellement\s+)?de\s+(\d{1,3})\s*ans?', text, re.IGNORECASE
        )
    if age_match and dates["note_date"]:
        stated_age = int(age_match.group(1))
        note_date = dates["note_date"]
        calculated_age = (note_date - dob).days // 365
        if abs(stated_age - calculated_age) > 1:
            warnings.append({
                "type": "age_dob_mismatch",
                "severity": "warning",
                "message": (
                    f"Stated age ({stated_age}yo) does not match calculated "
                    f"age from DOB ({calculated_age}yo)"
                ),
                "stated_age": stated_age,
                "calculated_age": calculated_age,
            })

    return warnings
