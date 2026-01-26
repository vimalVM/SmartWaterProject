from app.db import get_connection
from datetime import date, timedelta
import schedule, time


def process_day(archive_date):
    conn = get_connection()
    cur = conn.cursor()

    # archive per-tap usage
    cur.execute("""
        INSERT INTO tap_daily_archive (tap_id, usage_liters, archive_date)
        SELECT tap_id, current_usage, %s FROM tap_usage
    """, (archive_date,))

    # compute total
    cur.execute("SELECT SUM(current_usage) FROM tap_usage")
    total = cur.fetchone()[0] or 0

    # fetch config
    cur.execute("""
        SELECT users_count, green_limit_per_user, orange_limit_per_user
        FROM system_config WHERE id=1
    """)
    users, g, o = cur.fetchone()

    green_limit = users * g
    orange_limit = users * o

    if total <= green_limit:
        color = "GREEN"
    elif total <= orange_limit:
        color = "ORANGE"
    else:
        color = "RED"

    # save system total (safe upsert)
    cur.execute("""
        INSERT INTO system_daily_totals (total_usage, color_status, usage_date)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            total_usage = VALUES(total_usage),
            color_status = VALUES(color_status)
    """, (total, color, archive_date))

    # reset running usage
    cur.execute("UPDATE tap_usage SET current_usage = 0")

    conn.commit()
    conn.close()

    print(f"Archived & reset for {archive_date}")


def check_missed_midnight():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT MAX(usage_date) FROM system_daily_totals")
    last_aggregated = cur.fetchone()[0]

    yesterday = date.today() - timedelta(days=1)

    # First ever run → nothing to archive
    if last_aggregated is None:
        conn.close()
        return

    # Missed midnight → archive yesterday ONCE
    if last_aggregated < yesterday:
        process_day(yesterday)

    conn.close()


#  Run once on startup (handles missed midnight safely)
check_missed_midnight()

#  Schedule midnight aggregation (archives the day that just ended)
schedule.every().day.at("00:00").do(
    lambda: process_day(date.today() - timedelta(days=1))
)

while True:
    schedule.run_pending()
    time.sleep(1)
