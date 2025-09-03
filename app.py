import os
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify

app = Flask(__name__)
app.secret_key = "supersecret-key-change-this"  # change in production

# -----------------------------
# Storage (JSON – no database)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, "users.json")

SUBJECTS = ["Math", "Reading", "Writing", "English", "Computer", "Science", "Social"]

# -----------------------------
# Helpers
# -----------------------------
def ensure_store():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_users():
    ensure_store()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper

def current_user_full():
    if "user" not in session:
        return None
    username = session["user"]["username"]
    users = load_users()
    return next((u for u in users if u["username"].lower() == username.lower()), None)

# -----------------------------
# Recommendations / Badges / Points
# -----------------------------
RECOMMENDATIONS = {
    "Math": "Practice problem sets daily; revisit formulas and attempt past papers.",
    "Reading": "Read editorials and short stories; summarize in your own words.",
    "Writing": "Draft structured paragraphs; focus on grammar and clarity.",
    "English": "Improve vocabulary and grammar with short daily exercises.",
    "Computer": "Revise basics; build tiny programs or logic puzzles.",
    "Science": "Strengthen fundamentals; learn via concept maps and experiments.",
    "Social": "Create timelines/maps; revise key events and civics topics."
}

def make_recommendation(weakest_list, hours):
    if not weakest_list:
        base = "Great work! Keep practicing to maintain consistency."
    else:
        base = "; ".join(RECOMMENDATIONS.get(w, "Practice regularly.") for w in weakest_list)
    if hours < 2:
        return f"{base} You’re studying <2 hrs/day — try to increase consistent study time."
    if hours >= 6:
        return f"{base} You’re studying a lot — focus on targeted practice & mock tests."
    return base

def badge_for_percentage(p):
    if p >= 85:
        return "🏅 Gold"
    if p >= 70:
        return "🥈 Silver"
    if p >= 55:
        return "🥉 Bronze"
    return "🎯 Starter"

def clamp_scores(scores):
    return {k: max(0, min(100, int(v))) for k, v in scores.items()}

def compute_percentage(scores):
    return round(sum(scores.values()) / len(scores), 2) if scores else 0.0

def compute_points(prev_pct, new_pct):
    if new_pct > prev_pct:
        delta = new_pct - prev_pct
        if delta >= 10:
            return 20
        if delta >= 5:
            return 14
        return 10
    return 2

def compute_subject_deltas(prev_scores, new_scores):
    deltas = {}
    for s in SUBJECTS:
        prev = prev_scores.get(s, 0) if prev_scores else 0
        deltas[s] = new_scores.get(s, 0) - prev
    return deltas

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        users = load_users()
        user = next(
            (u for u in users if u["username"].lower() == username.lower() and u.get("password", "") == password),
            None
        )
        if user:
            session["user"] = {
                "username": user["username"],
                "name": user["name"],
                "roll": user["roll"]
            }
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials. Please try again.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        username = (request.form.get("username") or "").strip()
        roll = (request.form.get("roll") or "").strip()
        password = request.form.get("password") or ""
        repassword = request.form.get("repassword") or ""

        if not (name and username and roll and password and repassword):
            return render_template("register.html", error="All fields are required for registration.")

        if password != repassword:
            return render_template("register.html", error="Passwords do not match.")

        users = load_users()
        if any(u["username"].lower() == username.lower() for u in users):
            return render_template("register.html", error="Username already exists. Please choose another.")

        users.append({
            "name": name,
            "username": username,
            "roll": roll,
            "password": password,
            "points": 0,
            "records": []
        })
        save_users(users)
        return render_template("register.html", success="Registration successful. Please login.")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    user = current_user_full()
    if not user:
        return redirect(url_for("login"))

    latest = user["records"][-1] if user["records"] else None

    if request.method == "POST":
        try:
            hours = int(request.form.get("hours_studied", 0))
            scores = {
                "Math": int(request.form.get("math_score", 0)),
                "Reading": int(request.form.get("reading_score", 0)),
                "Writing": int(request.form.get("writing_score", 0)),
                "English": int(request.form.get("english_score", 0)),
                "Computer": int(request.form.get("computer_score", 0)),
                "Science": int(request.form.get("science_score", 0)),
                "Social": int(request.form.get("social_score", 0)),
            }
        except Exception:
            return render_template("home.html", user=user, latest=latest, error="Please enter valid integers (0–100).")

        scores = clamp_scores(scores)
        percentage = compute_percentage(scores)
        weakest_val = min(scores.values())
        weakest_subjects = sorted([s for s, v in scores.items() if v == weakest_val])
        recommendation = make_recommendation(weakest_subjects, hours)
        badge = badge_for_percentage(percentage)

        prev_pct = user["records"][-1]["percentage"] if user["records"] else 0
        prev_scores = user["records"][-1]["scores"] if user["records"] else {}
        points_gain = compute_points(prev_pct, percentage)
        deltas = compute_subject_deltas(prev_scores, scores)

        new_record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "hours": hours,
            "scores": scores,
            "percentage": percentage,
            "weakest_subjects": weakest_subjects,
            "recommendation": recommendation,
            "badge": badge,
            "deltas": deltas
        }

        users = load_users()
        for u in users:
            if u["username"].lower() == user["username"].lower():
                u["records"].append(new_record)
                u["points"] = u.get("points", 0) + points_gain
                user = u
                break
        save_users(users)
        latest = new_record

    trend_labels = []
    trend_percentages = []
    subject_trend = {s: [] for s in SUBJECTS}
    averages = {}

    if user["records"]:
        trend_labels = [f"Attempt {i+1}" for i in range(len(user["records"]))]  
        trend_percentages = [r["percentage"] for r in user["records"]]
        for s in SUBJECTS:
            subject_trend[s] = [r["scores"].get(s, 0) for r in user["records"]]
        averages = {
            s: round(sum(r["scores"].get(s, 0) for r in user["records"]) / len(user["records"]), 2)
            for s in SUBJECTS
        }

    scores_for_chart = latest["scores"] if latest else {}

    return render_template(
        "home.html",
        user=user,
        latest=latest,
        scores=scores_for_chart,
        trend={"labels": trend_labels, "percentages": trend_percentages},
        subject_trend=subject_trend,
        averages=averages
    )

@app.route("/records")
@login_required
def records():
    user = current_user_full()
    if not user:
        return redirect(url_for("login"))
    return render_template("records.html", user=user, records=user.get("records", []))

@app.route("/leaderboard")
def leaderboard():
    users = load_users()
    board = []
    for u in users:
        recs = u.get("records", [])
        if recs:
            avg = round(sum(r["percentage"] for r in recs) / len(recs), 2)
            board.append({
                "name": u.get("name", u["username"]),
                "roll": u.get("roll", "-"),
                "avg": avg,
                "points": u.get("points", 0)
            })
    board.sort(key=lambda x: (x["avg"], x["points"]), reverse=True)
    return render_template("leaderboard.html", leaderboard=board)

@app.route("/records/chart-data")
@login_required
def chart_data():
    user = current_user_full()
    if not user or not user.get("records"):
        return jsonify([])
    data = [
        {
            "timestamp": r["timestamp"],
            "percentage": r["percentage"],
            "scores": r["scores"]
        }
        for r in user["records"]
    ]
    return jsonify(data)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/static/<path:filename>")
def static_files(filename):
    static_dir = os.path.join(BASE_DIR, "static")
    return send_from_directory(static_dir, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
