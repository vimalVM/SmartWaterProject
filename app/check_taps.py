from app.db import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM taps")
count = cur.fetchone()[0]
conn.close()

print(count)
