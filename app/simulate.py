import random, time, schedule
from app.db import get_connection

def simulate_usage():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT tap_id FROM taps")
    taps = [row[0] for row in cur.fetchall()]

    for tap_id in taps:
        inc = random.uniform(2, 5)
        cur.execute(
            "UPDATE tap_usage SET current_usage = current_usage + %s, last_update=NOW() WHERE tap_id=%s",
            (round(inc,2), tap_id)
        )

    conn.commit()
    conn.close()
    print("Updated tap usage...")

schedule.every(1).minutes.do(simulate_usage)

while True:
    schedule.run_pending()
    time.sleep(1)
