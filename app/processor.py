from app.db import get_connection
from datetime import date
import schedule, time

def process_day():
    conn = get_connection()
    cur = conn.cursor()

    # archive per-tap usage
    cur.execute("""
        INSERT INTO tap_daily_archive (tap_id, usage_liters, archive_date)
        SELECT tap_id, current_usage, CURDATE() FROM tap_usage
    """)

    # compute total
    cur.execute("SELECT SUM(current_usage) FROM tap_usage")
    total = cur.fetchone()[0] or 0

    # fetch config
    cur.execute("SELECT users_count, green_limit_per_user, orange_limit_per_user FROM system_config WHERE id=1")
    users, g, o = cur.fetchone()

    green_limit = users * g
    orange_limit = users * o

    if total <= green_limit:
        color = "GREEN"
    elif total <= orange_limit:
        color = "ORANGE"
    else:
        color = "RED"

    # save system total
    cur.execute(
        "INSERT INTO system_daily_totals (total_usage, color_status, usage_date) VALUES (%s,%s,CURDATE())",
        (total, color)
    )

    # reset running usage
    cur.execute("UPDATE tap_usage SET current_usage=0")

    conn.commit()
    conn.close()
    print("Day archived & reset")

schedule.every().day.at("00:00").do(process_day)

while True:
    schedule.run_pending()
    time.sleep(1)
