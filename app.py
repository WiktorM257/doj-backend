from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from sqlalchemy import text
from database import get_conn, init_db

app = Flask(__name__)
CORS(app)

# INIT DB ON START
init_db()


# ------------------------------------------------
# GENERATE CASE ID
# ------------------------------------------------
def generate_case_id():
    year = datetime.now().year
    prefix = f"SA-{year}-"

    with get_conn() as conn:
        rows = conn.execute(
            text("SELECT id FROM schedule WHERE id LIKE :pfx"),
            {"pfx": f"{prefix}%"}
        ).fetchall()

    nums = []
    for r in rows:
        try:
            nums.append(int(r[0].split("-")[-1]))
        except:
            pass

    n = max(nums) + 1 if nums else 1
    return f"{prefix}{n:04d}"


# ------------------------------------------------
# ADD SCHEDULE
# ------------------------------------------------
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
        """), {"id": case_id, **data})

    return jsonify({"status": "ok", "added": {"id": case_id, **data}})


# ------------------------------------------------
# GET SCHEDULE
# ------------------------------------------------
@app.get("/schedule.json")
def get_schedule():
    with get_conn() as conn:
        rows = conn.execute(
            text("SELECT * FROM schedule ORDER BY date, time")
        ).fetchall()

    return jsonify([dict(r) for r in rows])


# ------------------------------------------------
# DELETE SCHEDULE
# ------------------------------------------------
@app.post("/api/delete_schedule")
def delete_schedule():
    case_id = request.json.get("id")

    with get_conn() as conn:
        conn.execute(text("DELETE FROM schedule WHERE id = :id"), {"id": case_id})

    return jsonify({"status": "deleted"})


# ------------------------------------------------
# ARCHIVE
# ------------------------------------------------
@app.post("/api/archive_case")
def archive_case():
    data = request.json
    case_id = data["id"]

    with get_conn() as conn:
        row = conn.execute(
            text("SELECT * FROM schedule WHERE id = :id"),
            {"id": case_id}
        ).fetchone()

        if not row:
            return jsonify({"status": "not_found"}), 404

        case = dict(row)

        conn.execute(text("DELETE FROM schedule WHERE id = :id"), {"id": case_id})

        conn.execute(text("""
            INSERT INTO archive (
                id, name, judge, prosecutor, defendant, lawyer,
                witnesses, room, date, time, parties, description,
                result, verdict, document
            ) VALUES (
                :id, :name, :judge, :prosecutor, :defendant, :lawyer,
                :witnesses, :room, :date, :time, :parties, :description,
                :result, :verdict, :document
            )
        """), {
            **case,
            "id": case_id,
            "result": data.get("result"),
            "verdict": data.get("verdict"),
            "document": data.get("document")
        })

    return jsonify({"status": "archived"})


# ------------------------------------------------
# GET ARCHIVE
# ------------------------------------------------
@app.get("/archive.json")
def get_archive():
    with get_conn() as conn:
        rows = conn.execute(
            text("SELECT * FROM archive ORDER BY date, time")
        ).fetchall()

    return jsonify([dict(r) for r in rows])


# ------------------------------------------------
# FORCE DROP schedule
# ------------------------------------------------
@app.get("/force-reset-schedule")
def force_reset_schedule():
    try:
        with get_conn() as conn:
            conn.execute(text("DROP TABLE IF EXISTS schedule CASCADE;"))
            conn.commit()
        return jsonify({"status": "ok", "message": "schedule table dropped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------
# FORCE CREATE schedule
# ------------------------------------------------
@app.get("/force-create-schedule")
def force_create_schedule():
    try:
        with get_conn() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    judge TEXT,
                    prosecutor TEXT,
                    defendant TEXT,
                    lawyer TEXT,
                    witnesses TEXT,
                    room TEXT,
                    date DATE,
                    time TIME,
                    parties TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """))
            conn.commit()
        return jsonify({"status": "ok", "message": "schedule table created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/debug-columns")
def debug_columns():
    try:
        with get_conn() as conn:
            result = conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type 
                FROM information_schema.columns
                WHERE table_name = 'schedule'
                ORDER BY ordinal_position;
            """))
            columns = []
            for row in result:
                columns.append({
                    "column_name": row[0],
                    "data_type": row[1]
                })
            return jsonify(columns)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------
# RUN
# ------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
