# Calendar Invite AI

A command-line tool that extracts meeting requests, deadlines, and responsibilities from `.docx` meeting notes and converts them into structured calendar events. The tool uses lightweight NLP and rule-based parsing to identify people, deadlines, and scheduling constraints. It generates a conflict-free `.ics` file that can be imported into Google Calendar, Outlook, or Microsoft Teams.

The scheduler automatically avoids weekends and US federal holidays and assigns meetings into structured 10–11 AM time slots while preventing scheduling conflicts. The purpose of the tool is to give people the option to upload their transcribed Teams .docx files from their meetings and automatically schedule those meetings in the command line.
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

