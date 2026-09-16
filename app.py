"""
RoughSet Challenge - Flask Web Application
A university-level interactive educational game for Rough Sets feature reduction.
"""

import csv
import io
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from config import Config
import database as db
import roughset as rs
import game_data as gd

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY


# ==========================================================
# CONTEXT PROCESSORS & AUTH HELPERS
# ==========================================================

@app.context_processor
def inject_global_state():
    """Injects current player info into all Jinja templates for the HUD."""
    player_id = session.get("player_id")
    player = db.get_player(player_id) if player_id else None
    return {
        "player": player,
        "is_admin": session.get("admin_authenticated", False)
    }


def student_required(f):
    """Requires an active student session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        player_id = session.get("player_id")
        if not player_id or not db.get_player(player_id):
            return redirect(url_for("join"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Requires instructor authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================================
# WEB VIEW ROUTES
# ==========================================================

@app.route("/")
def index():
    """Landing page with Hero and How It Works."""
    return render_template("index.html")


@app.route("/join", methods=["GET", "POST"])
def join():
    """Student entry point to join a live classroom challenge."""
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        first_name = request.form.get("first_name", "").strip()
        nickname = request.form.get("nickname", "").strip() or first_name

        if not code or not first_name:
            return render_template("join.html", error="Please enter both session code and first name.", code=code, first_name=first_name, nickname=nickname)

        classroom = db.get_classroom_by_code(code)
        if not classroom:
            return render_template("join.html", error="Challenge session not found. Please check your session code.", code=code, first_name=first_name, nickname=nickname)

        if not classroom.get("active"):
            return render_template("join.html", error="This classroom session has ended.", code=code, first_name=first_name, nickname=nickname)

        if not classroom.get("joining_open"):
            return render_template("join.html", error="Joining is currently closed for this challenge. Please ask your instructor.", code=code, first_name=first_name, nickname=nickname)

        # Create student in database
        player = db.create_player(classroom["id"], first_name, nickname)
        session["player_id"] = player["id"]
        session["classroom_id"] = classroom["id"]
        session["is_demo"] = False

        return redirect(url_for("mission"))

    return render_template("join.html")


@app.route("/mission")
@student_required
def mission():
    """Mission brief before timer starts."""
    return render_template("mission.html")


@app.route("/game/<int:level_num>")
@student_required
def game_level(level_num):
    """Renders Level 1, 2, 3, or 4."""
    if level_num == 1:
        return render_template("level1.html", level_data=gd.LEVEL_1_DATA, current_level_num=1)
    elif level_num == 2:
        return render_template("level2.html", level_data=gd.LEVEL_2_DATA, current_level_num=2)
    elif level_num == 3:
        return render_template("level3.html", level_data=gd.LEVEL_3_DATA, current_level_num=3)
    elif level_num == 4:
        return render_template("level4.html", level_data=gd.LEVEL_4_DATA, current_level_num=4)
    else:
        return redirect(url_for("quiz"))


@app.route("/quiz")
@student_required
def quiz():
    """Final 5-question comprehension quiz."""
    return render_template("quiz.html", questions=gd.QUIZ_QUESTIONS, current_level_num=5)


@app.route("/article")
def article_connection():
    """Visual bridge from game mechanics to the research paper."""
    return render_template("article_connection.html", comparisons=gd.ARTICLE_COMPARISONS)


@app.route("/result")
@student_required
def result():
    """Final summary of points, rank, time, and badges."""
    player_id = session.get("player_id")
    player = db.get_player(player_id)
    classroom_id = session.get("classroom_id")

    # Mark as completed if not yet marked
    if player and player.get("progress") and not player["progress"].get("completed"):
        db.complete_game(player_id)
        player = db.get_player(player_id)

    # Fetch leaderboard to get rank
    leaderboard = db.get_leaderboard(classroom_id) if classroom_id else []
    rank = next((p["rank"] for p in leaderboard if p["player_id"] == player_id), 1)
    
    # Calculate duration
    duration_formatted = "--:--"
    if player and player.get("progress"):
        started = player["progress"].get("started_at")
        completed = player["progress"].get("completed_at")
        if started and completed:
            try:
                from datetime import datetime
                s_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                c_dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                duration_formatted = db.format_duration((c_dt - s_dt).total_seconds())
            except Exception:
                pass

    return render_template("result.html", rank=rank, duration_formatted=duration_formatted)


@app.route("/leaderboard")
def leaderboard():
    """Projector-friendly live classroom rankings."""
    try:
        code_param = request.args.get("code", "").strip().upper()
        classroom = None

        # 1. Query parameter code (e.g. /leaderboard?code=RS8371)
        if code_param:
            classroom = db.get_classroom_by_code(code_param)

        # 2. Student session classroom_id
        if not classroom:
            classroom_id = session.get("classroom_id")
            if classroom_id:
                classroom = db.get_classroom_by_id(classroom_id)

        # 3. Instructor active admin code
        if not classroom:
            admin_code = session.get("active_admin_code")
            if admin_code:
                classroom = db.get_classroom_by_code(admin_code)

        # 4. Fallback to latest active/recent classroom
        if not classroom:
            classroom = db.get_latest_classroom()

        # 5. Fallback to demo classroom
        if not classroom:
            demo_class = db.get_classroom_by_code("DEMO99")
            if not demo_class:
                demo_class = db.create_classroom("DEMO99")
            classroom = demo_class

        classroom_id = classroom["id"] if classroom else None
        if classroom_id:
            session["classroom_id"] = classroom_id

        board_data = db.get_leaderboard(classroom_id) if classroom_id else []
        challenge_ended = not classroom.get("active", True) if classroom else False

        return render_template(
            "leaderboard.html",
            classroom=classroom,
            leaderboard=board_data,
            challenge_ended=challenge_ended
        )
    except Exception as e:
        app.logger.error(f"Error loading leaderboard: {e}")
        return render_template(
            "leaderboard.html",
            classroom={"code": "DEMO99", "active": True},
            leaderboard=[],
            challenge_ended=False
        )


# ==========================================================
# DEMO MODE (PRESENTER SANDBOX)
# ==========================================================

@app.route("/demo")
def demo():
    """Demo sandbox info screen."""
    return render_template("demo.html")


@app.route("/demo/start", methods=["POST"])
def demo_start():
    """Creates or joins an isolated demo session."""
    demo_classroom = db.get_classroom_by_code("DEMO99")
    if not demo_classroom:
        demo_classroom = db.create_classroom("DEMO99")

    demo_player = db.create_player(demo_classroom["id"], "Presenter_Demo", "Demo_User")
    session["player_id"] = demo_player["id"]
    session["classroom_id"] = demo_classroom["id"]
    session["is_demo"] = True

    # Start mission immediately
    db.start_player_mission(demo_player["id"])
    return redirect(url_for("game_level", level_num=1))


# ==========================================================
# INSTRUCTOR ADMIN PORTAL
# ==========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Teacher login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == Config.ADMIN_USERNAME and (password == Config.ADMIN_PASSWORD or Config.ADMIN_PASSWORD == ""):
            session["admin_authenticated"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid admin credentials.")

    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin_dashboard():
    """Instructor control room."""
    # Find currently active classroom or create default one
    active_code = session.get("active_admin_code")
    active_session = db.get_classroom_by_code(active_code) if active_code else None

    if not active_session:
        active_session = db.create_classroom()
        session["active_admin_code"] = active_session["code"]

    stats = db.get_classroom_stats(active_session["id"])

    return render_template(
        "admin.html",
        active_session=active_session,
        session_code=active_session["code"],
        stats=stats
    )


@app.route("/admin/create-session", methods=["POST"])
@admin_required
def admin_create_session():
    """Creates a new challenge session code."""
    new_sess = db.create_classroom()
    session["active_admin_code"] = new_sess["code"]
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/toggle-joining", methods=["POST"])
@admin_required
def admin_toggle_joining():
    """Toggles open/closed joining state."""
    open_val = request.form.get("joining_open") == "true"
    active_code = session.get("active_admin_code")
    sess = db.get_classroom_by_code(active_code) if active_code else None
    if sess:
        db.toggle_classroom_joining(sess["id"], open_val)
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/end-session", methods=["POST"])
@admin_required
def admin_end_session():
    """Ends the challenge session."""
    active_code = session.get("active_admin_code")
    sess = db.get_classroom_by_code(active_code) if active_code else None
    if sess:
        db.end_classroom(sess["id"])
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/export")
@admin_required
def admin_export():
    """Exports student results to CSV."""
    active_code = session.get("active_admin_code")
    sess = db.get_classroom_by_code(active_code) if active_code else None
    if not sess:
        return "No active session", 404

    board = db.get_leaderboard(sess["id"])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "First Name", "Nickname", "Score (XP)", "Duration (s)", "Duration Formatted", "Completed"])

    for p in board:
        writer.writerow([
            p["rank"],
            p["first_name"],
            p["nickname"],
            p["score"],
            p["duration_seconds"] or "",
            p["duration_formatted"],
            "Yes" if p["completed"] else "No"
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=roughset_results_{sess['code']}.csv"}
    )


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    return redirect(url_for("admin_login"))


# ==========================================================
# GAMEPLAY REST APIS (SERVER-AUTHORITATIVE)
# ==========================================================

@app.route("/api/start", methods=["POST"])
@student_required
def api_start_mission():
    """Starts the official server-side mission timer."""
    player_id = session.get("player_id")
    db.start_player_mission(player_id)
    return redirect(url_for("game_level", level_num=1))


@app.route("/api/check-feature", methods=["POST"])
@student_required
def api_check_feature():
    """
    Level 1: Checks if removing an attribute preserves classification power.
    Dispensable: +100 XP
    Indispensable: -25 XP penalty
    """
    player_id = session.get("player_id")
    body = request.get_json(force=True)
    level = body.get("level", 1)
    attr_to_remove = body.get("attribute")

    data = gd.LEVEL_1_DATA["objects"]
    all_attrs = gd.LEVEL_1_DATA["condition_attributes"]
    dec_attr = gd.LEVEL_1_DATA["decision_attribute"]

    dispensable = rs.is_dispensable(data, all_attrs, attr_to_remove, dec_attr)
    
    # Calculate reduced gamma
    remaining = [a for a in all_attrs if a != attr_to_remove]
    power = rs.dependency_degree(data, remaining, dec_attr)

    xp_awarded = 100 if dispensable else -25
    
    if dispensable:
        res = db.save_level_result(player_id, level_number=1, points_awarded=100)
    else:
        db.update_score_and_level(player_id, added_xp=-25)

    player = db.get_player(player_id)
    current_score = player["progress"]["score"] if player and player.get("progress") else 0

    return jsonify({
        "success": True,
        "dispensable": dispensable,
        "classification_power": power,
        "xp_awarded": xp_awarded,
        "total_score": current_score
    })


@app.route("/api/check-core", methods=["POST"])
@student_required
def api_check_core():
    """
    Level 2: Checks if an attribute belongs to the indispensable CORE.
    Indispensable: +150 XP
    Dispensable: 0 XP
    """
    player_id = session.get("player_id")
    body = request.get_json(force=True)
    attr = body.get("attribute")

    data = gd.LEVEL_2_DATA["objects"]
    all_attrs = gd.LEVEL_2_DATA["condition_attributes"]
    dec_attr = gd.LEVEL_2_DATA["decision_attribute"]

    is_indisp = rs.is_indispensable(data, all_attrs, attr, dec_attr)
    remaining = [a for a in all_attrs if a != attr]
    power = rs.dependency_degree(data, remaining, dec_attr)

    core_attrs = rs.find_core(data, all_attrs, dec_attr)

    xp_awarded = 150 if is_indisp else 0
    if is_indisp:
        db.update_score_and_level(player_id, added_xp=150)

    # Check if level completed bonus should be saved
    db.save_level_result(player_id, level_number=2, points_awarded=300)

    player = db.get_player(player_id)
    current_score = player["progress"]["score"] if player and player.get("progress") else 0

    return jsonify({
        "success": True,
        "is_indispensable": is_indisp,
        "classification_power": power,
        "xp_awarded": xp_awarded,
        "core_unlocked": True,
        "core": core_attrs,
        "total_score": current_score
    })


@app.route("/api/check-reduct", methods=["POST"])
@student_required
def api_check_reduct():
    """
    Levels 3 & 4: Evaluates candidate attribute subset against real Rough Sets.
    Valid REDUCT: +500 XP (L3) or +400 XP (L4) + bonuses
    """
    player_id = session.get("player_id")
    body = request.get_json(force=True)
    level = body.get("level", 3)
    candidate_attrs = body.get("attributes", [])
    attempts = body.get("attempts", 1)

    level_dict = gd.LEVEL_3_DATA if level == 3 else gd.LEVEL_4_DATA
    data = level_dict["objects"]
    full_attrs = level_dict["condition_attributes"]
    dec_attr = level_dict["decision_attribute"]

    is_valid, status, cand_gamma, tgt_gamma = rs.evaluate_candidate_reduct(
        data, candidate_attrs, full_attrs, dec_attr
    )

    xp_awarded = 0
    if is_valid:
        base_xp = 500 if level == 3 else 400
        # No incorrect attempts bonus
        attempt_bonus = 200 if attempts == 1 else 0
        xp_awarded = base_xp + attempt_bonus
        db.save_level_result(player_id, level_number=level, points_awarded=xp_awarded, attempts=attempts)

    reduction_pct = round(((len(full_attrs) - len(candidate_attrs)) / len(full_attrs)) * 100)

    player = db.get_player(player_id)
    current_score = player["progress"]["score"] if player and player.get("progress") else 0

    return jsonify({
        "success": True,
        "is_valid": is_valid,
        "status": status,
        "candidate_gamma": cand_gamma,
        "target_gamma": tgt_gamma,
        "reduction_percentage": reduction_pct,
        "xp_awarded": xp_awarded,
        "total_score": current_score
    })


@app.route("/api/quiz-answer", methods=["POST"])
@student_required
def api_quiz_answer():
    """Evaluates final quiz answers and prevents repeated question reward farming."""
    player_id = session.get("player_id")
    body = request.get_json(force=True)
    q_id = body.get("question_id")
    selected_key = body.get("selected_key")

    question = next((q for q in gd.QUIZ_QUESTIONS if q["id"] == q_id), None)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    is_correct = (question["correct_key"] == selected_key)
    res = db.save_quiz_answer(player_id, question_number=q_id, correct=is_correct, points=100)

    player = db.get_player(player_id)
    current_score = player["progress"]["score"] if player and player.get("progress") else 0

    return jsonify({
        "correct": is_correct,
        "points_awarded": res["points_awarded"],
        "already_answered": res["already_answered"],
        "explanation": question["explanation"],
        "total_score": current_score
    })


@app.route("/api/leaderboard")
def api_leaderboard():
    """Live polling endpoint for projector and client screens."""
    try:
        code_param = request.args.get("code", "").strip().upper()
        classroom = None

        if code_param:
            classroom = db.get_classroom_by_code(code_param)

        if not classroom:
            classroom_id = session.get("classroom_id")
            if classroom_id:
                classroom = db.get_classroom_by_id(classroom_id)

        if not classroom:
            admin_code = session.get("active_admin_code")
            if admin_code:
                classroom = db.get_classroom_by_code(admin_code)

        if not classroom:
            classroom = db.get_latest_classroom()

        if not classroom:
            demo_class = db.get_classroom_by_code("DEMO99")
            if not demo_class:
                demo_class = db.create_classroom("DEMO99")
            classroom = demo_class

        classroom_id = classroom["id"] if classroom else None
        board = db.get_leaderboard(classroom_id) if classroom_id else []
        challenge_ended = not classroom.get("active", True) if classroom else False

        return jsonify({
            "leaderboard": board,
            "challenge_ended": challenge_ended,
            "session_code": classroom.get("code") if classroom else ""
        })
    except Exception as e:
        app.logger.error(f"Error in api_leaderboard: {e}")
        return jsonify({
            "leaderboard": [],
            "challenge_ended": False
        })


@app.route("/api/player")
@student_required
def api_player():
    """Fetches current player score and status."""
    player_id = session.get("player_id")
    player = db.get_player(player_id)
    return jsonify({"player": player})


# ==========================================================
# MAIN EXECUTION
# ==========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
