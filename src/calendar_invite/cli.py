import sys

from .docx_reader import read_docx
from .extractor import process_sentences
from .calendar_export import create_ics


def main():
    # ---------------- CLI ARG CHECK ----------------
    if len(sys.argv) < 2:
        print("Usage: calendar-invite <file.docx>")
        sys.exit(1)

    file_path = sys.argv[1].strip()

    # ---------------- READ INPUT ----------------
    try:
        text = read_docx(file_path)
    except FileNotFoundError:
        print(f"Error: file not found -> {file_path}")
        sys.exit(1)

    # ---------------- PROCESS NLP ----------------
    intents = process_sentences(text)

    # ---------------- EMPTY SAFETY CHECK ----------------
    if not intents:
        print("No meeting intents found.")
        sys.exit(0)

    # ---------------- GENERATE ICS ----------------
    create_ics(intents)

    print(f"Done. Output written to output.ics ({len(intents)} meetings)")


if __name__ == "__main__":
    main()
