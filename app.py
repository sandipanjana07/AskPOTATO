from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import sqlite3
import os
import logging
from werkzeug.utils import secure_filename
from pathlib import Path

from config import Config
from askpotato.detector import detect_intent
from askpotato.retrieval import (
    handle_list_scenarios,
    handle_most_defects_scenario,
    handle_open_defects,
    handle_failed_steps,
    handle_no_proof_steps
)
from askpotato.explainer import explain_with_ai
from askpotato.normalizer import normalize_question

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
#UPLOAD
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_db_connection():
    """Create database connection with error handling"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def validate_scenario_form(form_data):
    """Validate scenario form inputs"""
    errors = []
    
    name = form_data.get('name', '').strip()
    if not name or len(name) < 3:
        errors.append("Scenario name must be at least 3 characters")
    
    area = form_data.get('area', '').strip()
    if not area:
        errors.append("Area is required")
    
    type_ = form_data.get('type', '').strip()
    if not type_:
        errors.append("Type is required")
    
    assigned_to = form_data.get('assigned_to', '').strip()
    if not assigned_to:
        errors.append("Assigned to is required")
    
    return errors, {
        'name': name,
        'area': area,
        'type': type_,
        'assigned_to': assigned_to
    }


@app.route("/")
def home():
    """Home page with AI assistant"""
    return render_template("index.html")


@app.route("/projects", methods=["GET", "POST"])
def projects():
    """Projects page - list and create scenarios"""
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        # validate form data
        errors, validated_data = validate_scenario_form(request.form)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            conn.close()
            return redirect(url_for("projects"))
        
        try:
            # insert new scenario
            cur.execute("""
                INSERT INTO scenarios (name, area, type, assigned_to, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (
                validated_data['name'],
                validated_data['area'],
                validated_data['type'],
                validated_data['assigned_to']
            ))

            scenario_id = cur.lastrowid

            # create default steps
            for i in range(1, app.config['DEFAULT_STEPS_COUNT'] + 1):
                cur.execute("""
                    INSERT INTO steps (scenario_id, step_number, step_name, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                """, (scenario_id, i, f"Step {i}"))

            conn.commit()
            flash(f"Scenario '{validated_data['name']}' created successfully!", 'success')
            logger.info(f"Created scenario: {validated_data['name']} (ID: {scenario_id})")
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error creating scenario: {e}")
            flash("Error creating scenario. Please try again.", 'error')
        finally:
            conn.close()

        return redirect(url_for("projects"))

    # pagination

    page = request.args.get('page', 1, type=int)
    per_page = app.config['SCENARIOS_PER_PAGE']
    offset = (page - 1) * per_page

    try:
        # get total count
        cur.execute("SELECT COUNT(*) as total FROM scenarios")
        total = cur.fetchone()['total']
        
        # get paginated scenarios
        cur.execute("""
            SELECT * FROM scenarios 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset))
        scenarios = cur.fetchall()
        
        # calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
    except sqlite3.Error as e:
        logger.error(f"Error fetching scenarios: {e}")
        flash("Error loading scenarios", 'error')
        scenarios = []
        total_pages = 1
        has_prev = has_next = False
    finally:
        conn.close()

    return render_template(
        "projects.html",
        scenarios=scenarios,
        page=page,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next
    )


@app.route("/scenarios/<int:scenario_id>")
def scenario_details(scenario_id):
    """Individual scenario details page"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # get scenario info
        cur.execute("""
            SELECT id, name, area, type, assigned_to, created_at
            FROM scenarios WHERE id = ?
        """, (scenario_id,))
        scenario = cur.fetchone()

        if not scenario:
            flash("Scenario not found", 'error')
            return redirect(url_for('projects'))

        # get steps
        cur.execute("""
            SELECT step_number, step_name, status, assigned_to
            FROM steps
            WHERE scenario_id = ?
            ORDER BY step_number
        """, (scenario_id,))
        steps = cur.fetchall()

        # get defects
        cur.execute("""
            SELECT id, step_number, title, status, reported_by, created_at
            FROM defects
            WHERE scenario_id = ?
            ORDER BY created_at DESC
        """, (scenario_id,))
        defects = cur.fetchall()

        # get proofs
        cur.execute("""
            SELECT step_number, filename, created_at
            FROM proofs
            WHERE scenario_id = ?
            ORDER BY created_at DESC
        """, (scenario_id,))
        proofs = cur.fetchall()

        # group by step
        defects_by_step = {}
        for d in defects:
            defects_by_step.setdefault(d["step_number"], []).append(d)

        proofs_by_step = {}
        for p in proofs:
            proofs_by_step.setdefault(p["step_number"], []).append(p)

    except sqlite3.Error as e:
        logger.error(f"Error fetching scenario details: {e}")
        flash("Error loading scenario details", 'error')
        return redirect(url_for('projects'))
    finally:
        conn.close()

    return render_template(
        "scenario_details.html",
        scenario=scenario,
        steps=steps,
        defects_by_step=defects_by_step,
        proofs_by_step=proofs_by_step
    )


@app.route("/update-step", methods=["POST"])
def update_step():
    """Update step status and assignee"""
    scenario_id = request.form.get("scenario_id")
    step_number = request.form.get("step_number")
    status = request.form.get("status")
    assigned_to = request.form.get("assigned_to", "").strip()

    if not all([scenario_id, step_number, status]):
        flash("Missing required fields", 'error')
        return redirect(url_for("projects"))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE steps
            SET status = ?, assigned_to = ?, updated_at = datetime('now')
            WHERE scenario_id = ? AND step_number = ?
        """, (status, assigned_to, scenario_id, step_number))

        conn.commit()
        flash(f"Step {step_number} updated", 'success')
        logger.info(f"Updated step {step_number} in scenario {scenario_id}")
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Error updating step: {e}")
        flash("Error updating step", 'error')
    finally:
        conn.close()

    return redirect(url_for("scenario_details", scenario_id=scenario_id))


@app.route("/add-defect", methods=["POST"])
def add_defect():
    """Add a new defect to a step"""
    scenario_id = request.form.get("scenario_id")
    step_number = request.form.get("step_number")
    title = request.form.get("title", "").strip()
    reported_by = request.form.get("reported_by", "").strip()

    if not title or len(title) < 5:
        flash("Defect title must be at least 5 characters", 'error')
        return redirect(url_for("scenario_details", scenario_id=scenario_id))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO defects (scenario_id, step_number, title, reported_by, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (scenario_id, step_number, title, reported_by))

        conn.commit()
        flash("Defect added successfully", 'success')
        logger.info(f"Added defect to step {step_number} in scenario {scenario_id}")
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Error adding defect: {e}")
        flash("Error adding defect", 'error')
    finally:
        conn.close()

    return redirect(url_for("scenario_details", scenario_id=scenario_id))


@app.route("/update-defect", methods=["POST"])
def update_defect():
    """Update defect status (close/reopen)"""
    defect_id = request.form.get("defect_id")
    scenario_id = request.form.get("scenario_id")
    new_status = request.form.get("status")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE defects 
            SET status = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (new_status, defect_id))

        conn.commit()
        flash(f"Defect marked as {new_status}", 'success')
        
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"Error updating defect: {e}")
        flash("Error updating defect", 'error')
    finally:
        conn.close()

    return redirect(url_for("scenario_details", scenario_id=scenario_id))


@app.route("/add-proof", methods=["POST"])
def add_proof():
    """Upload proof file for a step"""
    scenario_id = request.form.get("scenario_id")
    step_number = request.form.get("step_number")
    file = request.files.get("proof")

    if not file or file.filename == "":
        flash("No file selected", 'error')
        return redirect(url_for("scenario_details", scenario_id=scenario_id))

    if not allowed_file(file.filename):
        flash(f"Invalid file type. Allowed: {', '.join(app.config['ALLOWED_EXTENSIONS'])}", 'error')
        return redirect(url_for("scenario_details", scenario_id=scenario_id))

    try:
        filename = secure_filename(file.filename)
        # add timestamp to prevent overwriting
        timestamp = str(int(os.path.getmtime(__file__) * 1000))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO proofs (scenario_id, step_number, filename, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (scenario_id, step_number, filename))

        conn.commit()
        conn.close()
        
        flash("Proof uploaded successfully", 'success')
        logger.info(f"Uploaded proof for step {step_number} in scenario {scenario_id}")
        
    except Exception as e:
        logger.error(f"Error uploading proof: {e}")
        flash("Error uploading file", 'error')

    return redirect(url_for("scenario_details", scenario_id=scenario_id))


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/ask", methods=["GET", "POST"])
def ask():
    """AI assistant page - AskPOTATO"""
    response = ""
    loading = False

    if request.method == "POST":
        raw_question = request.form.get("question", "").strip()
        
        if not raw_question:
            flash("Please enter a question", 'error')
            return render_template("ask.html", response="")
        
        logger.info(f"Question asked: {raw_question}")
        
        try:
            normalized = normalize_question(raw_question)
            logger.info(f"Normalized to intent: {normalized}")

            intent = detect_intent(normalized)
            
            conn = get_db_connection()
            cur = conn.cursor()

            # route to appropriate handler
            if intent == "LIST_SCENARIOS":
                data = handle_list_scenarios(cur)
                response = explain_with_ai(raw_question, intent, data) if data else "No scenarios found."

            elif intent == "MOST_DEFECTS_SCENARIO":
                data = handle_most_defects_scenario(cur)
                response = explain_with_ai(raw_question, intent, data) if data else "No defects found."

            elif intent == "OPEN_DEFECTS":
                data = handle_open_defects(cur)
                response = explain_with_ai(raw_question, intent, data) if data else "No open defects."

            elif intent == "FAILED_STEPS":
                data = handle_failed_steps(cur)
                response = explain_with_ai(raw_question, intent, data) if data else "No failed steps."

            elif intent == "NO_PROOF_STEPS":
                data = handle_no_proof_steps(cur)
                response = explain_with_ai(raw_question, intent, data) if data else "All steps have proof uploaded."

            else:
                response = "I didn't quite understand that. Try asking about scenarios, defects, failed steps, or missing proofs."

            conn.close()
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            response = "Sorry, something went wrong processing your question. Please try again."
            flash("Error processing question", 'error')

    return render_template("ask.html", response=response)


@app.route("/api/scenarios", methods=["GET"])
def api_scenarios():
    """API endpoint to get scenarios as JSON"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM scenarios ORDER BY created_at DESC")
        scenarios = [dict(row) for row in cur.fetchall()]
        return jsonify({"scenarios": scenarios, "count": len(scenarios)})
    except sqlite3.Error as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal error: {error}")
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
