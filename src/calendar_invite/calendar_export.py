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
# DATE PARSING (FIXED LOGIC)
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

    # -------------------------
    # CASE 1: "next Friday" (FIXED: ALWAYS NEXT WEEK)
    # -------------------------
    match = re.search(r"\bnext\s+(monday|tuesday|wednesday|thursday|friday)", text)
    if match:
        day = weekday_map[match.group(1)]

        current_week_delta = day - transcript_date.weekday()
        if current_week_delta <= 0:
            current_week_delta += 7

        # FORCE NEXT WEEK (key fix)
        return transcript_date + timedelta(days=current_week_delta + 7)

    # -------------------------
    # CASE 2: "on Monday"
    # -------------------------
    match = re.search(r"\bon\s+(monday|tuesday|wednesday|thursday|friday)", text)
    if match:
        day = weekday_map[match.group(1)]
        delta = day - transcript_date.weekday()
        if delta <= 0:
            delta += 7
        return transcript_date + timedelta(days=delta)

    # -------------------------
    # CASE 3: "by Friday"
    # -------------------------
    match = re.search(r"\bby\s+(monday|tuesday|wednesday|thursday|friday)", text)
    if match:
        day = weekday_map[match.group(1)]
        delta = day - transcript_date.weekday()
        if delta <= 0:
            delta += 7
        return transcript_date + timedelta(days=delta)

    # -------------------------
    # CASE 4: bare weekday
    # -------------------------
    for name, day in weekday_map.items():
        if name in text:
            delta = day - transcript_date.weekday()
            if delta <= 0:
                delta += 7
            return transcript_date + timedelta(days=delta)

    return None


# =========================
# SCHEDULING SLOT
# =========================
def schedule_slot(date):
    start = datetime.combine(date.date(), time(10, 0))
    end = datetime.combine(date.date(), time(11, 0))
    return start, end


# =========================
# MAIN ICS EXPORT
# =========================
def create_ics(intents, output_file="output.ics"):
    cal = Calendar()
    cal.add("prodid", "-//calendar-invite//AI Parser//EN")
    cal.add("version", "2.0")

    transcript_date = datetime.now()
    current_day = next_business_day(transcript_date)

    for intent in intents:
        event = Event()

        # ---------------- SUMMARY ----------------
        if intent.meet_with:
            summary = f"Meet with {intent.meet_with}"
        elif intent.project_deadline:
            summary = "Project Deadline"
        else:
            summary = "Deadline Task"

        event.add("summary", summary)

        # ---------------- TARGET DATE ----------------
        target_date = parse_deadline(intent.deadline_to_meet, transcript_date)

        # ---------------- PICK DAY ----------------
        if target_date:
            meeting_day = target_date
        else:
            meeting_day = current_day

        # enforce business rules
        while is_invalid_day(meeting_day):
            meeting_day = next_business_day(meeting_day)

        # stagger meetings
        if meeting_day < current_day:
            meeting_day = current_day

        current_day = next_business_day(meeting_day)

        start, end = schedule_slot(meeting_day)

        # ---------------- EVENT ----------------
        event.add("dtstart", start)
        event.add("dtend", end)
        event.add("dtstamp", datetime.utcnow())
        event.add("uid", str(uuid.uuid4()))

        event.add(
            "description",
            "\n".join([
                f"Source sentence: {intent.raw_sentence or ''}",
                f"Deadline to meet: {intent.deadline_to_meet or 'None'}",
                f"Project deadline: {intent.project_deadline or 'None'}",
                f"Priority deadline: {intent.priority_deadline or 'None'}",
            ])
        )

        cal.add_component(event)

    with open(output_file, "wb") as f:
        f.write(cal.to_ical())
