from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "online_exam_secret_key"


def create_database():
    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("exam.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("exam.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email = ? AND password = ?",
            (email, password)
        )

        student = cursor.fetchone()
        conn.close()

        if student:
            session["student_name"] = student[1]
            return redirect("/exam")
        else:
            return "Invalid email or password!"

    return render_template("login.html")


@app.route("/exam")
def exam():
    return render_template("exam.html")


@app.route("/result", methods=["POST"])
def result():

    score = 0
    total = 3

    if request.form.get("q1") == "Python":
        score += 1

    if request.form.get("q2") == "a":
        score += 1

    if request.form.get("q3") == "CSS":
        score += 1

    percentage = (score / total) * 100

    if percentage >= 40:
        status = "Pass"
    else:
        status = "Fail"

    student_name = session.get("student_name")

    # Save result into database
    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO results
        (student_name, score, total, percentage, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_name,
        score,
        total,
        percentage,
        status
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage,
        status=status,
        student_name=student_name
    )
@app.route("/results")
def view_results():
    conn = sqlite3.connect("exam.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()

    conn.close()

    return render_template("results.html", results=results)

if __name__ == "__main__":
    create_database()
    app.run(debug=False)