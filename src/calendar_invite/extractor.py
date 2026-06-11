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


def process_sentences(text: str) -> List[CalendarIntent]:
    sentences = extract_sentences(text)

    results = []
    seen = set()

    for s in sentences:
        if s in seen:
            continue
        seen.add(s)

        meet_with = extract_person(s)

        # ONLY keep meeting intents
        if meet_with:
            intent = CalendarIntent()
            intent.raw_sentence = s
            intent.meet_with = meet_with
            results.append(intent)

    return results
