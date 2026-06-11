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


def adjust_to_business_day(dt):
    while is_invalid_day(dt):
        dt += timedelta(days=1)
    return dt


def next_business_day(dt):
    dt = dt + timedelta(days=1)
    return adjust_to_business_day(dt)


# =========================
# SLOT
# =========================
def meeting_slot(dt):
    start = datetime.combine(dt.date(), time(10, 0))
    end = datetime.combine(dt.date(), time(11, 0))
    return start, end


# =========================
# WEEKDAY MAP
# =========================
WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
}


# =========================
# CORE DATE RESOLUTION
# =========================
def resolve_weekday(weekday, transcript_date, mode="next"):
    """
    mode:
      - next: next occurrence
      - this: same week if possible
    """
    target_weekday = WEEKDAYS[weekday]
    current_weekday = transcript_date.weekday()

    if mode == "this":
        delta = target_weekday - current_weekday
        if delta < 0:
            delta += 7
    else:  # "next"
        delta = target_weekday - current_weekday
        if delta <= 0:
            delta += 7

    return transcript_date + timedelta(days=delta)


# =========================
# PARSER
# =========================
def extract_meeting_date(text, transcript_date):
    if not text:
        return None

    t = text.lower()

    modifier = None
    if "before " in t:
        modifier = "before"
    elif "by " in t:
        modifier = "by"
    elif "next " in t:
        modifier = "next"
    elif "this " in t:
        modifier = "this"

    weekday = None
    for w in WEEKDAYS:
        if re.search(rf"\b{w}\b", t):
            weekday = w
            break

    if not weekday:
        return None

    # resolve base date
    if modifier == "next":
        base = resolve_weekday(weekday, transcript_date, mode="next")

    elif modifier == "this":
        base = resolve_weekday(weekday, transcript_date, mode="this")
        if base < transcript_date:
            base = resolve_weekday(weekday, transcript_date, mode="next")

    else:
        # default + "by" behaves like target date
        base = resolve_weekday(weekday, transcript_date, mode="next")

    # apply BEFORE rule
    if modifier == "before":
        base -= timedelta(days=1)
        base = adjust_to_business_day(base)

    return base


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

        if not intent.meet_with:
            continue

        event = Event()
        event.add("summary", f"Meet with {intent.meet_with}")

        meeting_date = extract_meeting_date(
            intent.raw_sentence,
            transcript_date
        )

        if meeting_date:
            start, end = meeting_slot(meeting_date)
        else:
            start, end = meeting_slot(current_meeting_day)
            current_meeting_day = next_business_day(current_meeting_day)

        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("dtstamp", datetime.utcnow())
        event.add("uid", str(uuid.uuid4()))

        event.add(
            "description",
            f"Source sentence: {intent.raw_sentence or ''}\n"
            f"Meeting with: {intent.meet_with}\n"
        )

        cal.add_component(event)

    with open(output_file, "wb") as f:
        f.write(cal.to_ical())
