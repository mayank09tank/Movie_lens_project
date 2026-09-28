import os
import psycopg
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "movielens_secret_key_2024"

DB = dict(host="localhost", port=5432, dbname="movie_db", user="postgres", password="FB@hari3147")


def get_conn():
    return psycopg.connect(**DB, autocommit=False)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("auth_page"))
        return f(*args, **kwargs)
    return decorated


# ── Init users table ───────────────────────────────────────────────────────────
def init_users_table():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("user_ui"))
    return redirect(url_for("auth_page"))


@app.route("/auth")
def auth_page():
    if "user_id" in session:
        return redirect(url_for("user_ui"))
    return render_template("auth.html")


@app.route("/home")
@login_required
def user_ui():
    return render_template("user.html", user=session.get("user_name"), role=session.get("role"))


@app.route("/dev")
@login_required
def dev_ui():
    if session.get("role") != "admin":
        return redirect(url_for("user_ui"))
    return render_template("dev.html", user=session.get("user_name"))


# ── Auth APIs ──────────────────────────────────────────────────────────────────

@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.json
    name  = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    pwd   = data.get("password", "")
    if not name or not email or not pwd:
        return jsonify({"error": "All fields are required"}), 400
    if len(pwd) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                            (name, email, generate_password_hash(pwd)))
            conn.commit()
        return jsonify({"message": "Account created successfully!"}), 201
    except psycopg.errors.UniqueViolation:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/auth/login", methods=["POST"])
def login():
    data  = request.json
    email = data.get("email", "").strip().lower()
    pwd   = data.get("password", "")
    if not email or not pwd:
        return jsonify({"error": "All fields are required"}), 400
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, password_hash, role FROM users WHERE email=%s", (email,))
            row = cur.fetchone()
    if not row or not check_password_hash(row[2], pwd):
        return jsonify({"error": "Invalid email or password"}), 401
    session["user_id"]   = row[0]
    session["user_name"] = row[1]
    session["role"]      = row[3]
    return jsonify({"message": "Login successful", "name": row[1], "role": row[3]})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me")
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False})
    return jsonify({"logged_in": True, "name": session["user_name"], "role": session["role"]})


# ── Movies APIs ────────────────────────────────────────────────────────────────

@app.route("/api/movies/search")
@login_required
def search_movies():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT movie_id, title, genres FROM movies WHERE title ILIKE %s LIMIT 20", (f"%{q}%",))
            rows = cur.fetchall()
    return jsonify([{"movie_id": r[0], "title": r[1], "genres": r[2]} for r in rows])


@app.route("/api/movies")
@login_required
def get_movies():
    page   = int(request.args.get("page", 1))
    limit  = 20
    offset = (page - 1) * limit
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT movie_id, title, genres FROM movies ORDER BY movie_id LIMIT %s OFFSET %s", (limit, offset))
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM movies")
            total = cur.fetchone()[0]
    return jsonify({"movies": [{"movie_id": r[0], "title": r[1], "genres": r[2]} for r in rows], "total": total, "page": page})


@app.route("/api/movies", methods=["POST"])
@login_required
def add_movie():
    data = request.json
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO movies (movie_id, title, genres) VALUES (%s, %s, %s)",
                            (data["movie_id"], data["title"], data.get("genres", "")))
            conn.commit()
        return jsonify({"message": "Movie added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/movies/<int:movie_id>", methods=["PUT"])
@login_required
def update_movie(movie_id):
    data = request.json
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE movies SET title=%s, genres=%s WHERE movie_id=%s",
                            (data["title"], data.get("genres", ""), movie_id))
            conn.commit()
        return jsonify({"message": "Movie updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/movies/<int:movie_id>", methods=["DELETE"])
@login_required
def delete_movie(movie_id):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM movies WHERE movie_id=%s", (movie_id,))
            conn.commit()
        return jsonify({"message": "Movie deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    init_users_table()
    app.run(debug=True, port=5000)
