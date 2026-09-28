import os
import psycopg
import bcrypt
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from db import init_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="netflix_secret_key_2024")

UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

DB = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    dbname=os.getenv("DB_NAME", "movie_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
)

if not DB["password"]:
    raise RuntimeError("DB_PASSWORD is not set. Add it to movielens_app/.env or your environment.")


def get_conn():
    return psycopg.connect(**DB, autocommit=False)

def hash_password(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def verify_password(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def current_user(request: Request):
    return request.session.get("user")


# ── Setup ──────────────────────────────────────────────────────────────────────

def setup():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            SERIAL PRIMARY KEY,
                    name          TEXT NOT NULL,
                    email         TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role          TEXT DEFAULT 'user',
                    created_at    TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prompt_history (
                    id         SERIAL PRIMARY KEY,
                    user_id    INTEGER REFERENCES users(id),
                    question   TEXT NOT NULL,
                    answer     TEXT NOT NULL,
                    sources    TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS movie_history (
                    id         SERIAL PRIMARY KEY,
                    movie_id   INTEGER NOT NULL,
                    title      TEXT NOT NULL,
                    genres     TEXT,
                    action     TEXT NOT NULL,
                    changed_by TEXT,
                    changed_at TIMESTAMP DEFAULT NOW()
                )
            """)
        conn.commit()


setup()
init_db()


# ── Auth ───────────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "auth.html", {"tab": "login", "error": ""})


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    if current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "auth.html", {"tab": "signup", "error": ""})


@app.post("/login")
def do_login(request: Request, email: str = Form(...), password: str = Form(...)):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, password_hash, role FROM users WHERE email=%s", (email.lower(),))
            row = cur.fetchone()
    if not row or not verify_password(password, row[2]):
        return templates.TemplateResponse(request, "auth.html",
            {"tab": "login", "error": "Invalid email or password"})
    request.session["user"] = {"id": row[0], "name": row[1], "role": row[3]}
    return RedirectResponse("/", status_code=302)


@app.post("/signup")
def do_signup(request: Request, name: str = Form(...), email: str = Form(...),
              password: str = Form(...), confirm: str = Form(...)):
    if password != confirm:
        return templates.TemplateResponse(request, "auth.html",
            {"tab": "signup", "error": "Passwords do not match"})
    if len(password) < 6:
        return templates.TemplateResponse(request, "auth.html",
            {"tab": "signup", "error": "Password must be at least 6 characters"})
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                            (name.strip(), email.strip().lower(), hash_password(password)))
            conn.commit()
    except psycopg.errors.UniqueViolation:
        return templates.TemplateResponse(request, "auth.html",
            {"tab": "signup", "error": "Email already registered"})
    return templates.TemplateResponse(request, "auth.html",
        {"tab": "login", "error": "", "success": "Account created! Please login."})


@app.post("/logout")
def do_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# ── Home ───────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home(request: Request, q: str = "", genre: str = "", page: int = 1):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    limit, offset = 20, (page - 1) * 20
    with get_conn() as conn:
        with conn.cursor() as cur:
            filters, params = [], []
            if q:
                filters.append("title ILIKE %s"); params.append(f"%{q}%")
            if genre:
                filters.append("genres ILIKE %s"); params.append(f"%{genre}%")
            where = ("WHERE " + " AND ".join(filters)) if filters else ""
            cur.execute(f"SELECT COUNT(*) FROM movies {where}", params)
            total = cur.fetchone()[0]
            cur.execute(f"SELECT movie_id, title, genres FROM movies {where} ORDER BY movie_id LIMIT %s OFFSET %s",
                        params + [limit, offset])
            movies = [{"movie_id": r[0], "title": r[1], "genres": (r[2] or "").split("|")} for r in cur.fetchall()]
            cur.execute("SELECT DISTINCT unnest(string_to_array(genres, '|')) FROM movies ORDER BY 1")
            all_genres = [r[0] for r in cur.fetchall()]
    return templates.TemplateResponse(request, "home.html", {
        "movies": movies, "q": q, "genre": genre, "page": page,
        "total_pages": max(1, (total + limit - 1) // limit),
        "total": total, "all_genres": all_genres, "user": user,
    })


# ── T1: Admin Upload ───────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, msg: str = ""):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    if user["role"] != "admin":
        return RedirectResponse("/", status_code=302)
    files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse(request, "admin.html", {"user": user, "msg": msg, "files": files})


@app.post("/admin/upload")
async def admin_upload(request: Request, file: UploadFile = File(...)):
    user = current_user(request)
    if not user or user["role"] != "admin":
        return RedirectResponse("/login", status_code=302)
    if not file.filename.endswith(".pdf"):
        return RedirectResponse("/admin?msg=❌ Only PDF files allowed", status_code=303)
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())
    try:
        from rag.ingest import ingest_pdf
        chunks = ingest_pdf(save_path)
        return RedirectResponse(f"/admin?msg=✅ '{file.filename}' uploaded — {chunks} chunks indexed", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin?msg=❌ Upload ok but indexing failed: {e}", status_code=303)


# ── T5 + T7: Chat ──────────────────────────────────────────────────────────────

@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(request, "chat.html", {"user": user, "answer": None, "question": "", "chunks": []})


@app.post("/chat", response_class=HTMLResponse)
def chat_ask(request: Request, question: str = Form(...)):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    try:
        from rag.pipeline import answer_question
        answer, sources, documents = answer_question(question)
        chunks = [doc["text"] for doc in documents]
    except Exception as e:
        answer, chunks, sources = f"Error: {e}", [], []
    return templates.TemplateResponse(request, "chat.html", {
        "user": user, "answer": answer, "question": question, "chunks": chunks
    })


# ── T6: Prompt History ─────────────────────────────────────────────────────────

@app.get("/chat/history", response_class=HTMLResponse)
def chat_history(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    from db import get_history
    rows = get_history(limit=50)
    history = [
        {
            "question": r[1],
            "answer": r[2],
            "sources": r[3],
            "created_at": r[4].strftime("%d %b %Y %H:%M") if r[4] else ""
        }
        for r in rows
    ]
    return templates.TemplateResponse(request, "chat_history.html", {"user": user, "history": history})


# ── Dev Panel ──────────────────────────────────────────────────────────────────

def admin_required(request: Request):
    user = current_user(request)
    if not user:
        return None, RedirectResponse("/login", status_code=302)
    if user["role"] != "admin":
        return None, RedirectResponse("/", status_code=302)
    return user, None


@app.get("/dev", response_class=HTMLResponse)
def dev_panel(request: Request, msg: str = "", msg_type: str = "success"):
    user, redir = admin_required(request)
    if redir: return redir
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT movie_id, title, genres FROM movies ORDER BY movie_id DESC LIMIT 50")
            movies = [{"movie_id": r[0], "title": r[1], "genres": r[2] or ""} for r in cur.fetchall()]
            cur.execute("SELECT id, movie_id, title, genres, action, changed_by, changed_at FROM movie_history ORDER BY changed_at DESC LIMIT 50")
            history = [{"id": r[0], "movie_id": r[1], "title": r[2], "genres": r[3],
                        "action": r[4], "changed_by": r[5],
                        "changed_at": r[6].strftime("%d %b %Y %H:%M") if r[6] else ""} for r in cur.fetchall()]
    return templates.TemplateResponse(request, "dev.html", {
        "user": user, "movies": movies, "history": history, "msg": msg, "msg_type": msg_type
    })


@app.post("/dev/add")
def dev_add_movie(request: Request, title: str = Form(...), genres: str = Form(...)):
    user, redir = admin_required(request)
    if redir: return redir
    title, genres = title.strip(), genres.strip()
    if not title:
        return RedirectResponse("/dev?msg=❌ Title required&msg_type=error", status_code=303)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO movies (title, genres) VALUES (%s, %s) RETURNING movie_id", (title, genres))
            new_id = cur.fetchone()[0]
            cur.execute("INSERT INTO movie_history (movie_id, title, genres, action, changed_by) VALUES (%s, %s, %s, 'ADDED', %s)",
                        (new_id, title, genres, user["name"]))
        conn.commit()
    return RedirectResponse(f"/dev?msg=✅ Movie '{title}' added (ID: {new_id})", status_code=303)


@app.post("/dev/edit")
def dev_edit_movie(request: Request, movie_id: int = Form(...),
                   title: str = Form(...), genres: str = Form(...)):
    user, redir = admin_required(request)
    if redir: return redir
    title, genres = title.strip(), genres.strip()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT title, genres FROM movies WHERE movie_id = %s", (movie_id,))
            old = cur.fetchone()
            if not old:
                return RedirectResponse("/dev?msg=❌ Movie not found&msg_type=error", status_code=303)
            cur.execute("INSERT INTO movie_history (movie_id, title, genres, action, changed_by) VALUES (%s, %s, %s, 'BEFORE_EDIT', %s)",
                        (movie_id, old[0], old[1], user["name"]))
            cur.execute("UPDATE movies SET title=%s, genres=%s WHERE movie_id=%s", (title, genres, movie_id))
            cur.execute("INSERT INTO movie_history (movie_id, title, genres, action, changed_by) VALUES (%s, %s, %s, 'EDITED', %s)",
                        (movie_id, title, genres, user["name"]))
        conn.commit()
    return RedirectResponse(f"/dev?msg=✅ Movie ID {movie_id} updated", status_code=303)


@app.post("/dev/delete")
def dev_delete_movie(request: Request, movie_id: int = Form(...)):
    user, redir = admin_required(request)
    if redir: return redir
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT title, genres FROM movies WHERE movie_id = %s", (movie_id,))
            old = cur.fetchone()
            if not old:
                return RedirectResponse("/dev?msg=❌ Movie not found&msg_type=error", status_code=303)
            cur.execute("INSERT INTO movie_history (movie_id, title, genres, action, changed_by) VALUES (%s, %s, %s, 'DELETED', %s)",
                        (movie_id, old[0], old[1], user["name"]))
            cur.execute("DELETE FROM movies WHERE movie_id = %s", (movie_id,))
        conn.commit()
    return RedirectResponse(f"/dev?msg=✅ Movie '{old[0]}' deleted", status_code=303)






