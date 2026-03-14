import sqlite3
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

DB_PATH = "openclaw.db"  # 修改为你的数据库路径

app = Flask(__name__)
CORS(app)

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    one_min_ago = now - timedelta(minutes=1)

    cur.execute("""
        SELECT SUM(total_tokens) FROM usage
        WHERE timestamp >= ?
    """, (today_start.isoformat(),))
    today_total = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT model, SUM(total_tokens)
        FROM usage
        WHERE timestamp >= ?
        GROUP BY model
    """, (today_start.isoformat(),))
    by_model = dict(cur.fetchall())

    cur.execute("""
        SELECT SUM(total_tokens) FROM usage
        WHERE timestamp >= ?
    """, (one_min_ago.isoformat(),))
    rate = cur.fetchone()[0] or 0

    conn.close()

    return {
        "today_total": today_total,
        "rate_per_min": rate,
        "by_model": by_model
    }

@app.route("/stats")
def stats():
    return jsonify(get_stats())

if __name__ == "__main__":
    app.run(port=5000)
