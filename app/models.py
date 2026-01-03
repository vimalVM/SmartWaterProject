from app.db import get_connection

def get_config():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT users_count, green_limit_per_user, orange_limit_per_user FROM system_config WHERE id=1")
    data = cur.fetchone()
    conn.close()
    return data

def get_taps():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tap_id, tap_name FROM taps")
    rows = cur.fetchall()
    conn.close()
    return rows
