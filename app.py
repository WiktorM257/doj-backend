from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from database import get_conn, init_db
from sqlalchemy import text

app = Flask(__name__)
CORS(app)

# Init database
init_db()

# --------------------------------------
# Generate Case ID
# --------------------------------------
def generate_case_id():
    year = datetime.now().year
    prefix = f"SA-{year}-"

    with get_conn() as conn:
        result = conn.execute(text("""
            SELECT id FROM schedule WHERE id LIKE :pfx
        """), {"pfx": f"{prefix}%"}).fetchall()

    nums = []
    for row in result:
        try:
            nums.append(int(row[0].split("-")[-1]))
        except:
            pass

    next_number = max(nums) + 1 if nums else 1
    return f"{prefix}{next_number:04d}"


# --------------------------------------
# ADD SCHEDULE
# --------------------------------------
@app.post("/api/add_schedule")
def add_schedule():
    data = request.json
    case_id = generate_case_id()

    with get_conn() as conn:
        conn.execute(text("""
            INSERT INTO schedule (
                id, name, judge, prosecutor, defendant, lawyer,
                witnesses, room, date, time, parties, description
            ) VALUES (
                :id, :name, :judge, :prosecutor, :defendant, :lawyer,
                :witnesses, :room, :date, :time, :parties, :description
            )
        """), {
            "id": case_id,
            **data
        })

    return jsonify({"status": "ok", "added": {"id": case_id, **data}})


# --------------------------------------
# GET SCHEDULE
# --------------------------------------
@app.get("/schedule.json")
def get_schedule():
    with get_conn() as conn:
        rows = conn.execute(text("""
            SELECT * FROM schedule ORDER BY date, time
        """)).fetchall()

    return jsonify([dict(r) for r in rows])


# --------------------------------------
# DELETE SCHEDULE
# --------------------------------------
@app.post("/api/delete_schedule")
def delete_schedule():
    case_id = request.json.get("id")

    with get_conn() as conn:
        conn.execute(text("DELETE FROM schedule WHERE id = :id"), {"id": case_id})

    return jsonify({"status": "deleted"})


# --------------------------------------
# ARCHIVE CASE
# --------------------------------------
@app.post("/api/archive_case")
def archive_case():
    data = request.json
    case_id = data.get("id")

    with get_conn() as conn:

        row = conn.execute(text("""
            SELECT * FROM schedule WHERE id = :id
        """), {"id": case_id}).fetchone()

        if not row:
            return jsonify({"status": "not_found"}), 404

        case = dict(row)

        conn.execute(text("DELETE FROM schedule WHERE id = :id"), {"id": case_id})

        conn.execute(text("""
            INSERT INTO archive (
                id, name, judge, prosecutor, defendant, lawyer, witnesses,
                room, date, time, parties, description, result, verdict, document
            ) VALUES (
                :id, :name, :judge, :prosecutor, :defendant, :lawyer, :witnesses,
                :room, :date, :time, :parties, :description, :result, :verdict, :document
            )
        """), {
            "id": case_id,
            **case,
            "result": data.get("result"),
            "verdict": data.get("verdict"),
            "document": data.get("document")
        })

    return jsonify({"status": "archived"})


# --------------------------------------
# GET ARCHIVE
# --------------------------------------
@app.get("/archive.json")
def get_archive():
    with get_conn() as conn:
        rows = conn.execute(text("""
            SELECT * FROM archive ORDER BY date, time
        """)).fetchall()

    return jsonify([dict(r) for r in rows])

@app.get("/init-db")
def init_db_route():
    try:
        init_db()
        return jsonify({"status": "ok", "message": "Database initialized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --------------------------------------
# RUN
# --------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
