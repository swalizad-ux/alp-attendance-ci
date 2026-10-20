"""Integration tests: HTTP routes + store + attendance logic together."""


def make(client, path, **body):
    r = client.post(path, json=body)
    assert r.status_code == 201, r.get_json()
    return r.get_json()["id"]


def test_health(client):
    assert client.get("/health").get_json()["status"] == "ok"


def test_validation_errors(client):
    assert client.post("/students", json={"level": "Beginner"}).status_code == 400
    assert client.post("/students", json={"name": "X", "level": "Expert"}).status_code == 400
    assert client.post("/sessions", json={"level": "Beginner"}).status_code == 400


def test_checkin_rules(client):
    s = make(client, "/students", name="Amina", level="Beginner")
    adv = make(client, "/sessions", level="Advanced", date="2026-10-13")
    beg = make(client, "/sessions", level="Beginner", date="2026-10-13")
    assert client.post(f"/sessions/{adv}/checkins", json={"student_id": s}).status_code == 409
    assert client.post("/sessions/C9999/checkins", json={"student_id": s}).status_code == 404
    assert client.post(f"/sessions/{beg}/checkins", json={"student_id": s}).status_code == 201
    dup = client.post(f"/sessions/{beg}/checkins", json={"student_id": s})
    assert dup.status_code == 200 and dup.get_json()["duplicate"] is True


def test_report_flags_low_attendance(client):
    good = make(client, "/students", name="Fatima", level="Intermediate")
    low = make(client, "/students", name="Hamid", level="Intermediate")
    sessions = [make(client, "/sessions", level="Intermediate", date=f"2026-10-0{i}") for i in range(1, 5)]
    for c in sessions:
        client.post(f"/sessions/{c}/checkins", json={"student_id": good})
    client.post(f"/sessions/{sessions[0]}/checkins", json={"student_id": low})

    data = client.get("/reports/attendance").get_json()
    assert data["follow_up_count"] == 1
    first = data["students"][0]
    assert first["name"] == "Hamid" and first["rate"] == 0.25 and first["needs_follow_up"]
