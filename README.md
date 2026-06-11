# Calendar Invite AI

A command-line tool that extracts meeting requests, deadlines, and responsibilities from `.docx` meeting notes and converts them into structured calendar events. The tool uses lightweight NLP and rule-based parsing to identify people, deadlines, and scheduling constraints. It generates an`output.ics` file that can be imported into Google Calendar, Outlook, or Microsoft Teams with the command `open output.ics`.

Inspired by the Natural Language Date parser assignment 6, the purpose of the tool is to give people the option to upload their transcribed Teams .docx files from their meetings and automatically schedule those meetings in the command line before or on the date requested by, avoiding scheduling on holidays or weekends.

---

## Usage

### 1. Clone the repository, the sample.docx is for demo purposes but feel free
### to replace with your .docx file

```bash
git clone https://github.com/natalie3huynh/calendar-invite.git
cd calendar-invite
uv venv
uv sync
uv run python -m ensurepip --upgrade
uv run python -m pip install --upgrade pip
uv run python -m spacy download en_core_web_sm
uv run calendar-invite sample.docx

