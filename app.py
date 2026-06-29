import email

from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE = "database.db"


# ================= DATABASE CONNECTION =================
def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ================= CREATE TABLES =================
def create_tables():

    with get_db_connection() as conn:

        # USERS TABLE
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """)

        # COMPLAINTS TABLE
        conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Pending',
            location TEXT,
            ai_score INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()


create_tables()


# ================= HOME =================
@app.route("/about")
def about():

    return render_template("about.html")

@app.route("/")
def home():

    if "user" in session:

        if session["role"] == "admin":
            return redirect(url_for("admin"))

        else:
            return redirect(url_for("user_dashboard"))

    return redirect(url_for("login"))

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():


    if request.method == "POST":

        full_name = request.form["full_name"]

        email = request.form["email"]

        password = generate_password_hash(
            request.form["password"]
        )

        role = request.form["role"]

        with get_db_connection() as conn:

            existing = conn.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            ).fetchone()

            if existing:

                flash("Email already exists!")

                return redirect(url_for("register"))

            conn.execute("""
            INSERT INTO users
            (full_name, email, password, role)
            VALUES (?, ?, ?, ?)
            """, (
                full_name,
                email,
                password,
                role
            ))

            conn.commit()

        flash("Registration Successful!")

        return redirect(url_for("login"))

    return render_template("register.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        role = request.form["role"]

        with get_db_connection() as conn:

            user = conn.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            ).fetchone()

        if user and check_password_hash(
            user["password"],
            password
        ):

            if user["role"] == role:

                session["user"] = user["full_name"]

                session["role"] = user["role"]

                return redirect(url_for("home"))

        flash("Invalid Credentials!")

    return render_template("login.html")


# ================= USER DASHBOARD =================
@app.route("/user_dashboard")
def user_dashboard():

    if "user" not in session or session["role"] != "user":

        return redirect(url_for("login"))

    with get_db_connection() as conn:

        complaints = conn.execute("""
        SELECT * FROM complaints
        WHERE user_name=?
        ORDER BY created_at DESC
        """, (
            session["user"],
        )).fetchall()

    return render_template(
        "user_dashboard.html",
        complaints=complaints
    )


# ================= NEW COMPLAINT =================
@app.route("/new_complaint", methods=["GET", "POST"])
def new_complaint():

    if "user" not in session or session["role"] != "user":
        return redirect(url_for("login"))

    if request.method == "POST":
        tracking_id = "SGP" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]
        location = request.form["location"]

        evidence = request.files.get("evidence")

        filename = ""

        if evidence and evidence.filename != "":
            filename = secure_filename(evidence.filename)

            evidence.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        ai_score = 0

        text = description.lower()

        if "urgent" in text:
            ai_score += 40

        if "fraud" in text:
            ai_score += 30

        if "road" in text or "water" in text:
            ai_score += 20

        with get_db_connection() as conn:

            conn.execute("""
            INSERT INTO complaints
            (
                tracking_id,
                user_name,
                title,
                description,
                category,
                priority,
                location,
                evidence,
                ai_score
                         
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, 
            (
                tracking_id,
                session["user"],
                title,
                description,
                category,
                priority,
                location,
                filename,
                ai_score
            )
            )

            conn.commit()

        flash("Complaint Submitted Successfully!")

        return redirect(url_for("user_dashboard"))

    return render_template("new_complaint.html")

# ================= VIEW COMPLAINT =================
@app.route("/view/<int:id>", methods=["GET", "POST"])
def view_complaint(id):

    if "user" not in session:
        return redirect(url_for("login"))

    with get_db_connection() as conn:

        if request.method == "POST":

            reply = request.form["reply"]

            conn.execute(
                "UPDATE complaints SET reply=? WHERE id=?",
                (reply, id)
            )

            conn.commit()

            flash("Reply Sent Successfully")

        complaint = conn.execute(
            "SELECT * FROM complaints WHERE id=?",
            (id,)
        ).fetchone()

    return render_template(
        "view_complaint.html",
        complaint=complaint
    )

# ================= ADMIN DASHBOARD =================
@app.route("/admin")
def admin():

    if "user" not in session or session["role"] != "admin":

        return redirect(url_for("login"))

    # FILTER VALUES
    search = request.args.get("search", "")

    priority = request.args.get("priority", "")

    status = request.args.get("status", "")

    query = "SELECT * FROM complaints WHERE 1=1"

    values = []

    # SEARCH
    if search:

        query += " AND user_name LIKE ?"

        values.append(f"%{search}%")

    # PRIORITY FILTER
    if priority:

        query += " AND priority=?"

        values.append(priority)

    # STATUS FILTER
    if status:

        query += " AND status=?"

        values.append(status)

    query += " ORDER BY created_at DESC"

    with get_db_connection() as conn:

        complaints = conn.execute(
            query,
            values
        ).fetchall()

        total = conn.execute("""
        SELECT COUNT(*) FROM complaints
        """).fetchone()[0]

        pending = conn.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE status='Pending'
        """).fetchone()[0]

        resolved = conn.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE status='Resolved'
        """).fetchone()[0]

        high_priority = conn.execute("""
        SELECT COUNT(*) FROM complaints
        WHERE priority='High'
        """).fetchone()[0]

    high_percent = round(
        (high_priority / total) * 100,
        2
    ) if total else 0

    risk_level = (
        "High Risk"
        if high_percent > 40
        else "Low Risk"
    )

    return render_template(
        "admin.html",
        complaints=complaints,
        total=total,
        pending=pending,
        resolved=resolved,
        high_priority=high_priority,
        high_percent=high_percent,
        risk_level=risk_level
    )


# ================= UPDATE STATUS =================
@app.route("/update/<int:id>/<status>")
def update_status(id, status):

    if "user" not in session or session["role"] != "admin":

        return redirect(url_for("login"))

    with get_db_connection() as conn:

        conn.execute("""
        UPDATE complaints
        SET status=?
        WHERE id=?
        """, (
            status,
            id
        ))

        conn.commit()

    flash("Complaint Status Updated!")

    return redirect(url_for("admin"))


# ================= GENERATE FIR =================
@app.route("/generate_fir/<int:id>")
def generate_fir(id):

    if "user" not in session or session["role"] != "admin":

        return redirect(url_for("login"))

    with get_db_connection() as conn:

        complaint = conn.execute("""
        SELECT * FROM complaints
        WHERE id=?
        """, (
            id,
        )).fetchone()

    if not complaint:

        flash("Complaint not found!")

        return redirect(url_for("admin"))

    fir_text = f"""
FIR REPORT

Admin Name: {session['user']}

Complainant Name: {complaint['user_name']}

Complaint Title:
{complaint['title']}

Complaint Description:
{complaint['description']}

Category:
{complaint['category']}

Priority:
{complaint['priority']}

Location:
{complaint['location']}

Status:
{complaint['status']}

AI Score:
{complaint['ai_score']}

Generated By:
AI Smart Grievance System
"""

    return render_template(
        "fir.html",
        fir=fir_text
    )


@app.route("/download_fir/<int:id>")
def download_fir(id):

    with get_db_connection() as conn:

        complaint = conn.execute(
            "SELECT * FROM complaints WHERE id=?",
            (id,)
        ).fetchone()

    pdf_name = f"FIR_{id}.pdf"

    doc = SimpleDocTemplate(pdf_name)

    styles = getSampleStyleSheet()

    content = [

        Paragraph("SMART GRIEVANCE PORTAL FIR", styles["Title"]),

        Paragraph(
            f"Complaint ID: {complaint['id']}",
            styles["Normal"]
        ),

        Paragraph(
            f"Title: {complaint['title']}",
            styles["Normal"]
        ),

        Paragraph(
            f"Description: {complaint['description']}",
            styles["Normal"]
        ),

        Paragraph(
            f"Category: {complaint['category']}",
            styles["Normal"]
        ),

        Paragraph(
            f"Location: {complaint['location']}",
            styles["Normal"]
        ),

        Paragraph(
            f"Status: {complaint['status']}",
            styles["Normal"]
        ),

        Paragraph(
            f"Priority: {complaint['priority']}",
            styles["Normal"]
        )
    ]

    doc.build(content)

    return send_file(
        pdf_name,
        as_attachment=True
    )


# ================= FORGOT PASSWORD =================
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    ...

    if request.method == "POST":

        email = request.form["email"]

        new_password = generate_password_hash(
            request.form["new_password"]
        )

        with get_db_connection() as conn:

            user = conn.execute("""
            SELECT * FROM users
            WHERE email=?
            """, (
                email,
            )).fetchone()

            if not user:

                flash("Email not found!")

                return redirect(
                    url_for("forgot_password")
                )
            conn.execute("""
            UPDATE users
            SET password=?
            WHERE email=?
            """, (
            new_password,
            email
))
            conn.commit()

        flash("Password Updated Successfully!")

        return redirect(url_for("login"))

    return render_template("forgot_password.html")
@app.route("/track_complaint", methods=["GET", "POST"])
def track_complaint():

    complaint = None

    if request.method == "POST":

        tracking_id = request.form["tracking_id"]

        with get_db_connection() as conn:

            complaint = conn.execute(
                "SELECT * FROM complaints WHERE tracking_id=?",
                (tracking_id,)
            ).fetchone()

    return render_template(
        "track_complaint.html",
        complaint=complaint
    )
    

# ================= LOGOUT =================
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ================= RUN APP =================
if __name__ == "__main__":

    app.run(debug=True) 