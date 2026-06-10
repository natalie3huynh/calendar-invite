import re
from typing import List, Optional
import spacy

from .models import CalendarIntent

nlp = spacy.load("en_core_web_sm")

TRIGGERS = [
    "talk to",
    "speak to",
    "chat with",
    "meet with",
    "reach out to",
    "follow up with",
    "touchbase with",
]


def extract_sentences(text: str) -> List[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def extract_person(sentence: str) -> Optional[str]:
    lower = sentence.lower()

    for t in TRIGGERS:
        if t in lower:
            pattern = t + r"\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)"
            match = re.search(pattern, sentence)
            if match:
                return match.group(1).strip()

    return None


def extract_deadline(sentence: str) -> Optional[str]:
    patterns = [
        r"\bby\s+([A-Za-z0-9 ,]+?)(?:\.|,|$)",
        r"\bbefore\s+([A-Za-z0-9 ,]+?)(?:\.|,|$)",
        r"\bdeadline\s*[:\-]?\s+([A-Za-z0-9 ,]+?)(?:\.|,|$)",
    ]

    for p in patterns:
        match = re.search(p, sentence, re.IGNORECASE)
        if match:
            value = match.group(1).strip()

            # clean junk like "Wednesday about UX"
            value = re.split(r"\babout\b|\band\b|\bfor\b", value)[0].strip()

            return value

    return None


def process_sentences(text: str) -> List[CalendarIntent]:
    sentences = extract_sentences(text)

    results = []
    seen = set()

    for s in sentences:
        if s in seen:
            continue
        seen.add(s)

        intent = CalendarIntent()
        intent.raw_sentence = s

        intent.meet_with = extract_person(s)
        deadline = extract_deadline(s)

        if deadline:
            lower = s.lower()
            if "project" in lower:
                intent.project_deadline = deadline
            elif "priority" in lower:
                intent.priority_deadline = deadline
            else:
                intent.deadline_to_meet = deadline

        if (
            intent.meet_with
            or intent.deadline_to_meet
            or intent.project_deadline
            or intent.priority_deadline
        ):
            results.append(intent)

    return results
