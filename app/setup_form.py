from flask import Flask, request, render_template_string, redirect
from app.db import get_connection

app = Flask(__name__)

HTML = HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Water — System Setup</title>

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Icons -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">

<style>

/* ================= GLOBAL ================= */
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: "Segoe UI", system-ui, sans-serif;
    min-height: 100vh;
    background: linear-gradient(120deg, #4facfe, #00f2fe);
    animation: bgMove 10s infinite alternate;
    display: flex;
    align-items: center;
    justify-content: center;
}

@keyframes bgMove {
    0% { background-position: left; }
    100% { background-position: right; }
}

/* ================= CONTAINER ================= */
.container {
    width: 100%;
    padding: 20px;
    display: flex;
    justify-content: center;
}

/* ================= CARD ================= */
.card {
    width: 100%;
    max-width: 760px;
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(14px);
    border-radius: 22px;
    padding: 30px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.2);
    animation: slideUp 0.8s ease;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ================= HEADER ================= */
h2 {
    margin: 0;
    font-size: 26px;
}

.subtitle {
    font-size: 14px;
    color: #555;
    margin-bottom: 24px;
}

/* ================= FORM ================= */
.form-row {
    display: flex;
    gap: 18px;
    margin-bottom: 18px;
}

.form-group {
    flex: 1;
    position: relative;
}

/* Inputs */
.form-group input,
.form-group textarea {
    width: 100%;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid #d1d5db;
    font-size: 14px;
    background: transparent;
    outline: none;
    transition: 0.3s ease;
}

/* Autofill FIX (important) */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0px 1000px white inset;
    transition: background-color 5000s ease-in-out 0s;
}

.form-group textarea {
    height: 90px;
    resize: none;
}

/* Floating label */
.form-group label {
    position: absolute;
    top: 50%;
    left: 14px;
    color: #777;
    font-size: 13px;
    transform: translateY(-50%);
    background: white;
    padding: 0 6px;
    pointer-events: none;
    transition: 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.2);
}

/* Floating effect */
.form-group input:focus + label,
.form-group input:not(:placeholder-shown) + label,
.form-group textarea:focus + label,
.form-group textarea:not(:placeholder-shown) + label {
    top: -8px;
    font-size: 11px;
    color: #2563eb;
}

/* ================= DIVIDER ================= */
.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #ddd, transparent);
    margin: 24px 0;
}

/* ================= BUTTON ================= */
button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 16px;
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(37,99,235,0.45);
}

/* ================= NOTE ================= */
.note {
    font-size: 12px;
    color: #666;
    margin-top: 6px;
}

/* ================= RESPONSIVE ================= */
@media (max-width: 640px) {
    .form-row { flex-direction: column; }
    h2 { font-size: 22px; }
}

</style>
</head>

<body>

<div class="container">
<div class="card">

<h2> System Setup</h2>
<div class="subtitle">Configure users, limits, and tap details</div>

<form method="post" autocomplete="off">

<div class="form-row">
    <div class="form-group">
        <input type="number" name="users" placeholder=" " required>
        <label>Number of Users</label>
    </div>

    <div class="form-group">
        <input type="number" id="tapCount" name="tap_count" placeholder=" " required>
        <label>Number of Taps</label>

    </div>
</div>

<div class="divider"></div>

<div class="form-row">
    <div class="form-group">
        <input type="number" name="green" placeholder=" " required>
        <label>Green Limit per User (L)</label>
    </div>

    <div class="form-group">
        <input type="number" name="orange" placeholder=" " required>
        <label>Orange Limit per User (L)</label>
    </div>
</div>

<div class="divider"></div>

<div class="divider"></div>

<div id="tapContainer"></div>


<button type="submit">
    <i class="bi bi-check-circle"></i> Save & Continue
</button>

</form>

</div>
</div>

<script>
const tapCountInput = document.getElementById("tapCount");
const tapContainer = document.getElementById("tapContainer");

tapCountInput.addEventListener("input", () => {
    const count = parseInt(tapCountInput.value);
    tapContainer.innerHTML = "";

    if (!count || count <= 0) return;

    // Title
    const title = document.createElement("div");
    title.className = "subtitle";
    title.textContent = "Enter Tap Names";
    tapContainer.appendChild(title);

    for (let i = 1; i <= count; i++) {
        const group = document.createElement("div");
        group.className = "form-group";
        group.style.marginBottom = "14px";

        group.innerHTML = `
            <input type="text" name="tap_names[]" placeholder=" " required>
            <label>Tap ${i} Name</label>
        `;

        tapContainer.appendChild(group);
    }
});
</script>

</body>
</html>

"""


@app.route("/", methods=["GET","POST"])
def setup():
    if request.method == "POST":
        users = int(request.form["users"])
        green = float(request.form["green"])
        orange = float(request.form["orange"])

        # ✅ SAFETY FIX (no logic change)
        taps = [t.strip() for t in request.form.getlist("tap_names[]") if t.strip()]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO system_config
            (id, users_count, green_limit_per_user, orange_limit_per_user)
            VALUES (1, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                users_count = VALUES(users_count),
                green_limit_per_user = VALUES(green_limit_per_user),
                orange_limit_per_user = VALUES(orange_limit_per_user)
        """, (users, green, orange))

        cur.execute("DELETE FROM tap_usage")
        cur.execute("DELETE FROM taps")


        for name in taps:
            cur.execute("INSERT INTO taps (tap_name) VALUES (%s)", (name,))
            tap_id = cur.lastrowid
            cur.execute(
                "INSERT INTO tap_usage (tap_id, current_usage) VALUES (%s, 0)",
                (tap_id,)
            )

        conn.commit()
        conn.close()

        return redirect("/saved")

    return render_template_string(HTML)

@app.route("/saved")
def saved():
    return """
    <script>
        setTimeout(() => {
            window.location.replace("http://127.0.0.1:5000");
        }, 800);
    </script>
    """



if __name__ == "__main__":
    # Setup runs on a DIFFERENT port
    app.run(port=5001, debug=True, use_reloader=False)

