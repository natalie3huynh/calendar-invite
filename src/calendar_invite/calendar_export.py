from icalendar import Calendar, Event
from datetime import datetime, timedelta, time
import uuid
import re
import holidays

# =========================
# HOLIDAYS + VALID DAYS
# =========================
us_holidays = holidays.US()


def is_holiday(dt):
    return dt.date() in us_holidays


def is_weekend(dt):
    return dt.weekday() >= 5


def is_invalid_day(dt):
    return is_weekend(dt) or is_holiday(dt)


def next_business_day(dt):
    dt = dt + timedelta(days=1)
    while is_invalid_day(dt):
        dt += timedelta(days=1)
    return dt


# =========================
# DATE PARSING
# =========================
def parse_deadline(text, transcript_date):
    if not text:
        return None

    text = text.lower()

    weekday_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
    }

    # next Friday etc
    match = re.search(r"\bnext\s+(monday|tuesday|wednesday|thursday|friday)", text)
    if match:
        day = weekday_map[match.group(1)]
        delta = day - transcript_date.weekday()
        if delta <= 0:
            delta += 7
        return transcript_date + timedelta(days=delta + 7)

    # on Monday
    match = re.search(r"\bon\s+(monday|tuesday|wednesday|thursday|friday)", text)
    if match:
        day = weekday_map[match.group(1)]
        delta = day - transcript_date.weekday()
        if delta <= 0:
            delta += 7
        return transcript_date + timedelta(days=delta)

    # by Friday
    match = re.search(r"\bby\s+(monday|tuesday|wednesday|thursday|friday)", text)
    if match:
        day = weekday_map[match.group(1)]
        delta = day - transcript_date.weekday()
        if delta <= 0:
            delta += 7
        return transcript_date + timedelta(days=delta)

    # bare weekday
    for name, day in weekday_map.items():
        if name in text:
            delta = day - transcript_date.weekday()
            if delta <= 0:
                delta += 7
            return transcript_date + timedelta(days=delta)

    # IMPORTANT: keep explicit dates like "June 20th"
    match = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})", text)
    if match:
        month = match.group(1)
        day = int(match.group(2))

        month_map = {
            "june": 6,
            "july": 7,
        }

        year = transcript_date.year
        return datetime(year, month_map[month], day)

    return None


# =========================
# SLOT HELPERS
# =========================
def meeting_slot(dt):
    start = datetime.combine(dt.date(), time(10, 0))
    end = datetime.combine(dt.date(), time(11, 0))
    return start, end


def deadline_slot(dt):
    start = datetime.combine(dt.date(), time(8, 0))
    end = datetime.combine(dt.date(), time(9, 0))
    return start, end


# =========================
# MAIN EXPORT
# =========================
def create_ics(intents, output_file="output.ics"):
    cal = Calendar()
    cal.add("prodid", "-//calendar-invite//AI Parser//EN")
    cal.add("version", "2.0")

    transcript_date = datetime.now()
    current_meeting_day = next_business_day(transcript_date)

    for intent in intents:
        event = Event()

        # ---------------- CLASSIFY ----------------
        is_deadline = (
            intent.project_deadline
            or intent.priority_deadline
            or (intent.deadline_to_meet and "due" in intent.raw_sentence.lower())
        )

        # ---------------- SUMMARY ----------------
        if intent.meet_with:
            summary = f"Meet with {intent.meet_with}"
        else:
            summary = "Deadline Task"

        event.add("summary", summary)

        # ---------------- DEADLINES (FIXED: NO SHIFTING) ----------------
        if is_deadline:
            target = parse_deadline(
                intent.deadline_to_meet
                or intent.project_deadline
                or intent.priority_deadline,
                transcript_date
            )

            if target:
                start, end = deadline_slot(target)
            else:
                start, end = deadline_slot(transcript_date)

        # ---------------- MEETINGS ----------------
        else:
            start, end = meeting_slot(current_meeting_day)
            current_meeting_day = next_business_day(current_meeting_day)

        # ---------------- EVENT ----------------
        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("dtstamp", datetime.utcnow())
        event.add("uid", str(uuid.uuid4()))

        event.add(
            "description",
            f"Source sentence: {intent.raw_sentence or ''}\n"
            f"Deadline to meet: {intent.deadline_to_meet or 'None'}\n"
            f"Project deadline: {intent.project_deadline or 'None'}\n"
            f"Priority deadline: {intent.priority_deadline or 'None'}"
        )

        cal.add_component(event)

    with open(output_file, "wb") as f:
        f.write(cal.to_ical())
