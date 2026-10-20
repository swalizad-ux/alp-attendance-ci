from flask import Blueprint, current_app, jsonify, request

from .attendance import FOLLOW_UP_THRESHOLD, summarize

bp = Blueprint("alp", __name__)


def store():
    return current_app.config["STORE"]


@bp.get("/health")
def health():
    return {"status": "ok", "service": "alp-attendance"}


@bp.post("/students")
def create_student():
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "").strip()
    if not name:
        return {"error": "name is required"}, 400
    try:
        sid = store().add_student(name, body.get("level"))
    except ValueError as e:
        return {"error": str(e)}, 400
    return {"id": sid, "name": name, "level": body["level"]}, 201


@bp.post("/sessions")
def create_session():
    body = request.get_json(silent=True) or {}
    if not body.get("date"):
        return {"error": "date is required"}, 400
    try:
        cid = store().add_session(body.get("level"), body["date"])
    except ValueError as e:
        return {"error": str(e)}, 400
    return {"id": cid, **store().sessions[cid]}, 201


@bp.post("/sessions/<session_id>/checkins")
def check_in(session_id):
    body = request.get_json(silent=True) or {}
    try:
        new = store().check_in(session_id, body.get("student_id"))
    except KeyError as e:
        return {"error": e.args[0]}, 404
    except ValueError as e:
        return {"error": str(e)}, 409
    return {"checked_in": True, "duplicate": not new}, 201 if new else 200


@bp.get("/reports/attendance")
def report():
    s = store()
    rows = summarize(s.students, s.sessions, s.checkins)
    return jsonify(
        threshold=FOLLOW_UP_THRESHOLD,
        students=[
            {
                "id": r.student_id,
                "name": r.name,
                "level": r.level,
                "attended": r.attended,
                "held": r.held,
                "rate": round(r.rate, 2),
                "needs_follow_up": r.needs_follow_up,
            }
            for r in rows
        ],
        follow_up_count=sum(r.needs_follow_up for r in rows),
    )
