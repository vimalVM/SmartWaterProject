from flask import Blueprint
from app.db import get_connection

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/api/usage_by_day")
def usage_by_day():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT usage_date, total_usage
        FROM system_daily_totals
        ORDER BY usage_date
    """)
    rows = cur.fetchall()
    conn.close()

    return {
        "labels": [str(r[0]) for r in rows],
        "values": [float(r[1]) for r in rows]
    }


@reports_bp.route("/api/usage_by_tap")
def usage_by_tap():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.tap_name, u.current_usage
        FROM taps t
        JOIN tap_usage u ON t.tap_id = u.tap_id
    """)
    rows = cur.fetchall()
    conn.close()

    return {
        "labels": [r[0] for r in rows],
        "values": [float(r[1]) for r in rows]
    }


@reports_bp.route("/api/insights")
def insights():
    conn = get_connection()
    cur = conn.cursor()

    # today usage
    cur.execute("SELECT SUM(current_usage) FROM tap_usage")
    today = cur.fetchone()[0] or 0

    # yesterday usage
    cur.execute("""
        SELECT total_usage
        FROM system_daily_totals
        ORDER BY usage_date DESC
        LIMIT 1 OFFSET 1
    """)
    row = cur.fetchone()
    yesterday = row[0] if row else 0

    change = ((today - yesterday) / yesterday * 100) if yesterday else 0

    conn.close()

    return {
        "avg": round(today, 2),
        "change": round(change, 2)
    }
