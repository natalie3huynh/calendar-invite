from typing import Optional


class CalendarIntent:
    def __init__(self):
        self.meet_with: Optional[str] = None
        self.raw_sentence: Optional[str] = None

    def to_dict(self):
        return {
            "meet_with": self.meet_with,
            "raw_sentence": self.raw_sentence,
        }
