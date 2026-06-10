import sys

from .docx_reader import read_docx
from .extractor import process_sentences
from .calendar_export import create_ics


def main():
    # ---------------- CLI ARG CHECK ----------------
    if len(sys.argv) < 2:
        print("Usage: calendar-invite <file.docx>")
        sys.exit(1)

    file_path = sys.argv[1]

    # ---------------- READ INPUT ----------------
    try:
        text = read_docx(file_path)
    except FileNotFoundError:
        print(f"Error: file not found -> {file_path}")
        sys.exit(1)

    # ---------------- PROCESS NLP ----------------
    intents = process_sentences(text)

    # ---------------- GENERATE ICS ----------------
    create_ics(intents)

    print("Done. Output written to output.ics")
