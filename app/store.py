"""In-memory store; swapped for PostgreSQL in the full capstone platform."""

import itertools
import threading

VALID_LEVELS = {"Beginner", "Intermediate", "Advanced"}


class Store:
    def __init__(self):
        self.students: dict[str, dict] = {}
        self.sessions: dict[str, dict] = {}
        self.checkins: set[tuple[str, str]] = set()
        self._ids = itertools.count(1)
        self._lock = threading.Lock()

    def _next(self, prefix):
        return f"{prefix}{next(self._ids):04d}"

    def add_student(self, name, level):
        if level not in VALID_LEVELS:
            raise ValueError(f"level must be one of {sorted(VALID_LEVELS)}")
        with self._lock:
            sid = self._next("S")
            self.students[sid] = {"name": name, "level": level}
            return sid

    def add_session(self, level, date):
        if level not in VALID_LEVELS:
            raise ValueError(f"level must be one of {sorted(VALID_LEVELS)}")
        with self._lock:
            sess = self._next("C")
            self.sessions[sess] = {"level": level, "date": date}
            return sess

    def check_in(self, session_id, student_id):
        if session_id not in self.sessions:
            raise KeyError("unknown session")
        if student_id not in self.students:
            raise KeyError("unknown student")
        if self.sessions[session_id]["level"] != self.students[student_id]["level"]:
            raise ValueError("student is not enrolled in this class level")
        with self._lock:
            new = (session_id, student_id) not in self.checkins
            self.checkins.add((session_id, student_id))
            return new
