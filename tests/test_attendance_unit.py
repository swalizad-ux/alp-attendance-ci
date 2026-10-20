"""Unit tests: pure attendance logic, no HTTP."""

from app.attendance import StudentSummary, summarize


def test_rate_and_threshold():
    assert StudentSummary("S1", "A", "Beginner", 3, 4).needs_follow_up is False  # 75% is OK
    assert StudentSummary("S2", "B", "Beginner", 2, 4).needs_follow_up is True


def test_no_sessions_is_not_flagged():
    s = StudentSummary("S1", "A", "Beginner", 0, 0)
    assert s.rate == 0.0 and s.needs_follow_up is False


def test_only_own_level_sessions_count():
    students = {"S1": {"name": "Amina", "level": "Beginner"}}
    sessions = {"C1": {"level": "Beginner", "date": "d"}, "C2": {"level": "Advanced", "date": "d"}}
    [row] = summarize(students, sessions, {("C1", "S1")})
    assert (row.attended, row.held, row.rate) == (1, 1, 1.0)


def test_sorted_lowest_attendance_first():
    students = {"S1": {"name": "Zahra", "level": "Beginner"}, "S2": {"name": "Omar", "level": "Beginner"}}
    sessions = {"C1": {"level": "Beginner", "date": "d"}, "C2": {"level": "Beginner", "date": "d"}}
    rows = summarize(students, sessions, {("C1", "S1"), ("C2", "S1"), ("C1", "S2")})
    assert [r.name for r in rows] == ["Omar", "Zahra"]
