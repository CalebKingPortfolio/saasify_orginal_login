import os
import sqlite3
from flask import Flask, render_template, session, redirect, request, abort
from datetime import timedelta
import logging
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask("SaaSify Local Login")
app.secret_key = "esc70wegQpJ9jTBia4eWEdpqy9r49cAU"
app.permanent_session_lifetime = timedelta(minutes=15)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

logging.basicConfig(
    filename='login_events.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@admin",))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("Test1234@4&g")
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", ("admin@admin", hashed_pw))
    conn.commit()
    conn.close()

init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row and check_password_hash(row[0], password):
            session.permanent = True
            session["user_email"] = email
            session["user_name"] = "Admin"

            user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            logging.info(
                f"User {email} (Admin) logged in from IP {user_ip}"
            )
            return redirect("/protected_area")
        else:
            return render_template("index.html", error="Invalid email or password")

    return render_template("index.html")


@app.route("/protected_area")
def protected_area():
    if "user_email" not in session:
        return redirect("/")
    return render_template("protected_area.html", user_name=session["user_name"])


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
