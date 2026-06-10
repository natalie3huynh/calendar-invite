from typing import Optional


class CalendarIntent:
    def __init__(self):
        self.meet_with: Optional[str] = None
        self.deadline_to_meet: Optional[str] = None
        self.project_deadline: Optional[str] = None
        self.priority_deadline: Optional[str] = None
        self.raw_sentence: Optional[str] = None

    def to_dict(self):
        return {
            "meet_with": self.meet_with,
            "deadline_to_meet": self.deadline_to_meet,
            "project_deadline": self.project_deadline,
            "priority_deadline": self.priority_deadline,
            "raw_sentence": self.raw_sentence,
        }
