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

    # total usage today + tap count
    cur.execute("""
        SELECT 
            SUM(current_usage), 
            COUNT(*)
        FROM tap_usage
    """)
    total, tap_count = cur.fetchone()
    total = total or 0
    tap_count = tap_count or 1

    avg = total / tap_count

    # yesterday total usage
    cur.execute("""
        SELECT total_usage
        FROM system_daily_totals
        ORDER BY usage_date DESC
        LIMIT 1 OFFSET 1
    """)
    row = cur.fetchone()
    yesterday = row[0] if row else 0

    change = ((total - yesterday) / yesterday * 100) if yesterday else 0

    conn.close()

    return {
        "avg": round(avg, 2),
        "change": round(change, 2)
    }
@reports_bp.route("/api/usage_10min")
def usage_10min():
    from flask import request
    conn = get_connection()
    cur = conn.cursor()

    range_opt = request.args.get("range", "24h")

    interval_map = {
        "1h":  "1 HOUR",
        "3h":  "3 HOUR",
        "6h":  "6 HOUR",
        "12h": "12 HOUR",
        "24h": "24 HOUR"
    }

    interval = interval_map.get(range_opt, "24 HOUR")

    cur.execute(f"""
        SELECT
            recorded_at,
            SUM(usage_liters)
        FROM tap_usage_timeseries
        WHERE recorded_at >= NOW() - INTERVAL {interval}
        GROUP BY recorded_at
        ORDER BY recorded_at
    """)

    rows = cur.fetchall()
    conn.close()

    return {
        "labels": [r[0].strftime("%H:%M") for r in rows],
        "data": [float(r[1]) for r in rows]
    }

