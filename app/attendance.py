"""Pure attendance logic (no Flask) so it can be unit-tested in isolation."""

from dataclasses import dataclass

FOLLOW_UP_THRESHOLD = 0.75  # below 75% attendance -> instructor/manager follow-up


@dataclass(frozen=True)
class StudentSummary:
    student_id: str
    name: str
    level: str
    attended: int
    held: int

    @property
    def rate(self) -> float:
        return 0.0 if self.held == 0 else self.attended / self.held

    @property
    def needs_follow_up(self) -> bool:
        # A student with no sessions yet can't be flagged.
        return self.held > 0 and self.rate < FOLLOW_UP_THRESHOLD


def summarize(students, sessions, checkins):
    """Build per-student summaries.

    students: {id: {"name", "level"}}
    sessions: {session_id: {"level", "date"}}
    checkins: set of (session_id, student_id)
    Only sessions for the student's own class level count toward 'held'.
    """
    out = []
    for sid, s in students.items():
        held = [x for x, sess in sessions.items() if sess["level"] == s["level"]]
        attended = sum(1 for x in held if (x, sid) in checkins)
        out.append(StudentSummary(sid, s["name"], s["level"], attended, len(held)))
    return sorted(out, key=lambda r: (r.rate, r.name))
