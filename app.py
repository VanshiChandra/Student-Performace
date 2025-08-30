import os, json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecret-key-change-this"

USERS_FILE = "users.json"

# ---------- Storage helpers ----------
def ensure_store():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_users():
    ensure_store()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# ---------- Recommendation & badges ----------
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

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # One page for Login + Register (name, username, roll, password, re-enter)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        roll = request.form.get("roll", "").strip()
        password = request.form.get("password", "")
        repassword = request.form.get("repassword", "")
        action = request.form.get("action", "login")

        users = load_users()

        if action == "register":
            if not (name and username and roll and password and repassword):
                return render_template("login.html", error="All fields are required for registration.")
            if password != repassword:
                return render_template("login.html", error="Passwords do not match.")
            if any(u["username"].lower() == username.lower() for u in users):
                return render_template("login.html", error="Username already exists.")
            users.append({
                "name": name,
                "username": username,
                "roll": roll,
                "password": password,
                "points": 0,
                "records": []   # each record: {timestamp, hours, scores{}, percentage, weakest[], badge}
            })
            save_users(users)
            return render_template("login.html", success="Registration successful. Please log in.")

        # login
        user = next((u for u in users if u["username"] == username and u["password"] == password), None)
        if user:
            session["user"] = {"username": user["username"]}  # keep session light
            return redirect(url_for("home"))
        return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")

def current_user_full():
    """Return full user dict from store for the logged-in user (or None)."""
    if "user" not in session:
        return None
    username = session["user"]["username"]
    users = load_users()
    return next((u for u in users if u["username"] == username), None)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/home", methods=["GET", "POST"])
def home():
    user = current_user_full()
    if not user:
        return redirect(url_for("login"))

    users = load_users()

    # Defaults for rendering
    latest = user["records"][-1] if user["records"] else None
    trend_labels = []
    trend_percentages = []
    subject_trend = {}  # per subject list

    if request.method == "POST":
        # read scores + hours
        try:
            scores = {
                "Math": int(request.form.get("math_score", 0)),
                "Reading": int(request.form.get("reading_score", 0)),
                "Writing": int(request.form.get("writing_score", 0)),
                "English": int(request.form.get("english_score", 0)),
                "Computer": int(request.form.get("computer_score", 0)),
                "Science": int(request.form.get("science_score", 0)),
                "Social": int(request.form.get("social_score", 0)),
            }
            hours = int(request.form.get("hours_studied", 0))
        except Exception:
            return render_template("home.html",
                                   user=user,
                                   error="Please enter valid integers for hours and all subject scores (0–100).")

        # clamp 0..100
        scores = {k: max(0, min(100, v)) for k, v in scores.items()}
        percentage = round(sum(scores.values()) / len(scores), 2)
        weakest_subjects = [s for s, v in scores.items() if v == min(scores.values())]
        recommendation = make_recommendation(weakest_subjects, hours)
        badge = badge_for_percentage(percentage)

        # points (based on improvement)
        prev_pct = user["records"][-1]["percentage"] if user["records"] else 0
        points_gain = 10 if percentage > prev_pct else 2

        new_record = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
            "hours": hours,
            "scores": scores,
            "percentage": percentage,
            "weakest_subjects": weakest_subjects,
            "recommendation": recommendation,
            "badge": badge
        }

        # save back
        for u in users:
            if u["username"] == user["username"]:
                u["records"].append(new_record)
                u["points"] = u.get("points", 0) + points_gain
                user = u  # refresh the local copy for render
                break
        save_users(users)

        latest = new_record

    # Prepare trend + subject trend for charts
    if user["records"]:
        trend_labels = [f"Attempt {i+1}" for i in range(len(user["records"]))]
        trend_percentages = [r["percentage"] for r in user["records"]]
        # build subject trend
        subjects = ["Math", "Reading", "Writing", "English", "Computer", "Science", "Social"]
        for s in subjects:
            subject_trend[s] = [r["scores"][s] for r in user["records"]]

    # averages for bar compare
    if user["records"]:
        all_subjects = ["Math","Reading","Writing","English","Computer","Science","Social"]
        avg_scores = {s: round(sum(r["scores"][s] for r in user["records"]) / len(user["records"]), 2) for s in all_subjects}
    else:
        avg_scores = {}

    # Build chart payloads (dicts -> JSON via Jinja automatically)
    scores_for_chart = latest["scores"] if latest else {}
    trend_for_chart = {
        "labels": trend_labels,
        "percentages": trend_percentages
    }
    subject_trend_for_chart = subject_trend
    averages_for_chart = avg_scores

    return render_template(
        "home.html",
        user=user,
        latest=latest,
        scores=scores_for_chart,
        trend=trend_for_chart,
        subject_trend=subject_trend_for_chart,
        averages=averages_for_chart
    )

@app.route("/records")
def records():
    user = current_user_full()
    if not user:
        return redirect(url_for("login"))
    return render_template("records.html", user=user, records=user["records"])

@app.route("/leaderboard")
def leaderboard():
    # show name, roll, avg%, points — only shows users who have records
    users = load_users()
    board = []
    for u in users:
        recs = u.get("records", [])
        if recs:
            avg = round(sum(r["percentage"] for r in recs) / len(recs), 2)
            board.append({
                "name": u["name"],
                "roll": u["roll"],
                "avg": avg,
                "points": u.get("points", 0)
            })
    board.sort(key=lambda x: (x["avg"], x["points"]), reverse=True)
    return render_template("leaderboard.html", leaderboard=board)

if __name__ == "__main__":
    app.run(debug=True)
