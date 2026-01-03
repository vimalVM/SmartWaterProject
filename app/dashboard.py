from flask import Flask, render_template_string, request
from app.reports import reports_bp
from app.db import get_connection

app = Flask(__name__)
app.register_blueprint(reports_bp)


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Water Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Bootstrap 5 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Icons -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">

<style>
body {
    background: linear-gradient(135deg, #eef2f7, #f9fbff);
    font-family: "Segoe UI", sans-serif;
}

/* HEADER */
.dashboard-header {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.15);
}

/* STATUS BADGE ANIMATION */
.badge-animated {
    padding: 8px 16px;
    border-radius: 50px;
    font-size: 14px;
    font-weight: 700;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.08); opacity: 1; }
    100% { transform: scale(1); opacity: 0.9; }
}

.bg-green { background: #1fa463; }
.bg-orange { background: #f5a524; }
.bg-red { background: #d93025; }

/* CARD */
.card-custom {
    border-radius: 16px;
    border: none;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    transition: transform 0.3s ease;
    height: 100%;
}


.card-custom:hover {
    transform: translateY(-6px);
}

/* TAP STATUS */
.tap-green { color: #1fa463; }
.tap-orange { color: #d88700; }
.tap-red { color: #d93025; }

/* PROGRESS */
.progress {
    height: 10px;
    border-radius: 20px;
}

.progress-bar {
    transition: width 1.2s ease-in-out;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin: 20px 0 12px;
    color: #222;
}

.add-tap-card {
    border: 2px dashed #4facfe;
    border-radius: 16px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    transition: 0.3s;
}


.add-tap-card:hover {
    background: #f0f8ff;
}

.add-circle {
    width: 52px;
    height: 52px;
    background: #4facfe;
    color: white;
    border-radius: 50%;
    font-size: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}


.footer {
    font-size: 13px;
    color: #666;
}
</style>
</head>

<body>

<div class="container py-4">

<!-- HEADER -->
<div class="dashboard-header mb-4">
    <div class="row align-items-center">
        <div class="col-md-8">
            <h2 class="fw-bold mb-1">
                <i class="bi bi-droplet-half"></i> Smart Water Usage Dashboard
            </h2>
            <p class="mb-0">Live monitoring of water consumption</p>
        </div>
        <div class="col-md-4 text-md-end mt-3 mt-md-0">
            <h5>Total Usage Today</h5>
            <h3 class="fw-bold">{{ total }} L</h3>

            {% if color == 'GREEN' %}
                <span class="badge-animated bg-green">GREEN</span>
            {% elif color == 'ORANGE' %}
                <span class="badge-animated bg-orange">ORANGE</span>
            {% else %}
                <span class="badge-animated bg-red">RED</span>
            {% endif %}
        </div>
    </div>
</div>

    <!-- TAPS -->
    <!-- TAP USAGE -->
<div class="section-title">Tap Usage</div>

    <div class="row g-4 align-items-center">

        {% for t in taps %}
        <div class="col-md-4">
            <div class="card card-custom p-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h5 class="fw-bold mb-0">
                        <i class="bi bi-faucet"></i> {{ t[0] }}
                    </h5>

                    {% if t[2] == 'GREEN' %}
                        <span class="tap-green fw-bold">GREEN</span>
                    {% elif t[2] == 'ORANGE' %}
                        <span class="tap-orange fw-bold">ORANGE</span>
                    {% else %}
                        <span class="tap-red fw-bold">RED</span>
                    {% endif %}
                </div>

                <p class="mb-2">Usage: <b>{{ "%.2f"|format(t[1]) }} L</b></p>
                <!-- PROGRESS BAR (KEPT) -->
                <div class="progress">
                    {% if t[2] == 'GREEN' %}
                        <div class="progress-bar bg-success" style="width:40%"></div>
                    {% elif t[2] == 'ORANGE' %}
                        <div class="progress-bar bg-warning" style="width:70%"></div>
                    {% else %}
                        <div class="progress-bar bg-danger" style="width:95%"></div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}

        <!-- ADD TAP CARD -->
        <div class="col-md-4">
            <div class="card add-tap-card" onclick="openAddTap()">
                <div class="add-circle">+</div>
                <div class="fw-bold mt-2">Add Tap</div>
            </div>
        </div>

    </div>


<!-- REPORTS -->
<div class="section-title mt-5">Reports</div>

<div class="row g-4">

    <!-- LINE CHART -->
    <div class="col-md-4">
        <div class="card card-custom p-3">
            <h6 class="fw-bold mb-2">Usage Over Time</h6>
            <canvas id="lineChart"></canvas>
        </div>
    </div>

    <!-- BAR CHART -->
    <div class="col-md-4">
        <div class="card card-custom p-3">
            <h6 class="fw-bold mb-2">Daily Totals</h6>
            <canvas id="barChart"></canvas>
        </div>
    </div>

    <!-- PIE CHART -->
    <div class="col-md-4">
        <div class="card card-custom p-3">
            <h6 class="fw-bold mb-2">Usage by Tap</h6>
            <canvas id="pieChart"></canvas>
        </div>
    </div>

</div>

<!-- INSIGHTS -->
<div class="section-title mt-5">Water Saving Insights</div>

<div class="row g-4">

    <div class="col-md-6">
        <div class="card card-custom p-3 text-center">
            <h6 class="fw-bold">Average Consumption Today</h6>
            <h3 id="avgUsage">--</h3>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card card-custom p-3 text-center">
            <h6 class="fw-bold">Change vs Yesterday</h6>
            <h3 id="changeUsage">--</h3>
        </div>
    </div>

</div>
</div>

<!-- FOOTER -->
<div class="text-center mt-4 footer">
    <i class="bi bi-arrow-repeat"></i> Auto-refresh every 60 seconds
</div>

<meta http-equiv="refresh" content="60">

</div>

<script>

/* LINE + BAR CHART */
fetch("/api/usage_by_day")
.then(res => res.json())
.then(data => {
    new Chart(document.getElementById("lineChart"), {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Usage (L)",
                data: data.values,
                borderColor: "#4facfe",
                tension: 0.4
            }]
        }
    });

    new Chart(document.getElementById("barChart"), {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Daily Total (L)",
                data: data.values,
                backgroundColor: "#00c9a7"
            }]
        }
    });
});

/* PIE CHART */
fetch("/api/usage_by_tap")
.then(res => res.json())
.then(data => {
    new Chart(document.getElementById("pieChart"), {
        type: "pie",
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values
            }]
        }
    });
});

/* INSIGHTS */
fetch("/api/insights")
.then(res => res.json())
.then(data => {
    document.getElementById("avgUsage").innerText = data.avg + " L";
    document.getElementById("changeUsage").innerText = data.change + " %";
});


function openAddTap() {
    const name = prompt("Enter new tap name:");
    if (!name) return;

    fetch("/add_tap", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name})
    }).then(() => location.reload());
}
</script>


</body>
</html>

"""


@app.route("/")
def home():
    conn = get_connection()
    cur = conn.cursor()

    # ensure taps exist
    cur.execute("SELECT COUNT(*) FROM taps")
    if cur.fetchone()[0] == 0:
        return """
        <script>
        window.location.replace("http://127.0.0.1:5001");
        </script>
        """


    # fetch system limits
    cur.execute(
        "SELECT users_count, green_limit_per_user, orange_limit_per_user "
        "FROM system_config WHERE id=1"
    )
    row = cur.fetchone()
    if not row:
        return "<h3>System not configured. Please run setup_form.</h3>"

    users, g, o = row

    # ----- thresholds WITH user scaling -----
    tap_green_limit  = users * g
    tap_orange_limit = users * o
    system_green     = users * g
    system_orange    = users * o

    # fetch tap usage
    cur.execute("""
        SELECT t.tap_name, u.current_usage
        FROM taps t
        JOIN tap_usage u ON t.tap_id = u.tap_id
    """)

    taps = []
    total_usage = 0

    for name, usage in cur.fetchall():
        usage = usage or 0
        total_usage += usage

        # per-tap color (user-scaled)
        if usage <= tap_green_limit:
            tap_color = "GREEN"
        elif usage <= tap_orange_limit:
            tap_color = "ORANGE"
        else:
            tap_color = "RED"

        taps.append((name, usage, tap_color))

    # system-level color
    if total_usage <= system_green:
        system_color = "GREEN"
    elif total_usage <= system_orange:
        system_color = "ORANGE"
    else:
        system_color = "RED"

    conn.close()

    return render_template_string(
        HTML,
        taps=taps,
        total=round(total_usage, 2),
        color=system_color
    )

@app.route("/add_tap", methods=["POST"])
def add_tap():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return "", 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO taps (tap_name) VALUES (%s)", (name,))
    tap_id = cur.lastrowid

    cur.execute(
        "INSERT INTO tap_usage (tap_id, current_usage) VALUES (%s, 0)",
        (tap_id,)
    )

    conn.commit()
    conn.close()
    return "", 204



if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)

