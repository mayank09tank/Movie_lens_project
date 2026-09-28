# MovieLens Web Application — Complete Documentation

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [System Architecture](#4-system-architecture)
5. [Database Design](#5-database-design)
6. [Backend — FastAPI](#6-backend--fastapi)
7. [Frontend — Jinja2 + CSS](#7-frontend--jinja2--css)
8. [Authentication System](#8-authentication-system)
9. [Request Flow](#9-request-flow)
10. [API Routes Reference](#10-api-routes-reference)
11. [How to Run](#11-how-to-run)

---

## 1. Project Overview

MovieLens is a Netflix-style web application built on top of the MovieLens dataset stored in PostgreSQL.

**Two types of users:**

| User Type | What they can do |
|-----------|--------------------|
| Regular User | Sign up, Login, Browse movies, Search, Filter by genre |
| Developer | All of the above + Add, Edit, Delete movies, View change history |

---

## 2. Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI (Python) | Fast, modern, async-ready Python web framework |
| Database | PostgreSQL | Relational DB, supports triggers for history tracking |
| DB Driver | psycopg3 | Latest PostgreSQL driver for Python |
| Templates | Jinja2 | Server-side HTML rendering with Python data |
| Styling | Plain CSS | Netflix-style dark theme, no external CSS framework |
| Auth | bcrypt + SessionMiddleware | Secure password hashing + session-based login |
| Server | Uvicorn | ASGI server to run FastAPI |

---

## 3. Project Structure

```
movielens_app/
│
├── main.py                  ← Entire backend (routes, DB, auth, setup)
│
├── requirements.txt         ← Python dependencies
│
├── .env                     ← DB credentials (not committed to git)
│
├── static/
│   └── css/
│       └── style.css        ← All styling (Netflix dark theme)
│
└── templates/
    ├── base.html            ← Shared navbar layout (parent template)
    ├── home.html            ← Movie grid page (extends base.html)
    └── auth.html            ← Login + Signup page (standalone)
```

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        BROWSER                          │
│                                                         │
│   User visits URL → sends HTTP request                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    FASTAPI (main.py)                     │
│                                                         │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │   Routes    │   │     Auth     │   │   DB Layer  │  │
│  │             │   │              │   │             │  │
│  │  GET /      │   │  bcrypt hash │   │  get_conn() │  │
│  │  GET /login │   │  session mgmt│   │  psycopg3   │  │
│  │  POST /login│   │  middleware  │   │             │  │
│  │  GET /signup│   └──────────────┘   └──────┬──────┘  │
│  │  POST/signup│                             │         │
│  └──────┬──────┘                             │         │
│         │                                   │         │
│         ▼                                   ▼         │
│  ┌─────────────┐                   ┌──────────────┐   │
│  │   Jinja2    │                   │  PostgreSQL  │   │
│  │  Templates  │◄──── data ────────│              │   │
│  │             │                   │  movies      │   │
│  │  base.html  │                   │  users       │   │
│  │  home.html  │                   └──────────────┘   │
│  │  auth.html  │                                      │
│  └──────┬──────┘                                      │
│         │ HTML                                        │
└─────────┼───────────────────────────────────────────--┘
          │ HTTP Response (HTML page)
          ▼
┌─────────────────────────────────────────────────────────┐
│                        BROWSER                          │
│                   Renders HTML + CSS                    │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Database Design

### `movies`
```sql
CREATE TABLE movies (
    movie_id  INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    genres    TEXT
);
```

### `users`
```sql
CREATE TABLE users (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL,
    email          TEXT UNIQUE NOT NULL,
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMP DEFAULT NOW()
);
```

---

## 6. Backend — FastAPI

**App initialization:**
```python
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="...")
app.mount("/static", StaticFiles(...))
templates = Jinja2Templates(...)
```

**DB Connection:**
```python
DB = dict(host="localhost", port=5432, dbname="movie_db", ...)

def get_conn():
    return psycopg.connect(**DB, autocommit=False)
```

---

## 7. Frontend — Jinja2 + CSS

### Template Inheritance
```
base.html  (parent)
    │
    ├── home.html   (extends base)
    │
    └── auth.html   (standalone)
```

### CSS Design System
```
Background  →  #141414  (Netflix dark)
Text        →  #e5e5e5
Accent      →  #e50914  (Netflix red)
Card BG     →  #1f1f1f
```

---

## 8. Authentication System

```
SIGNUP:  POST /signup → bcrypt hash → INSERT users → redirect login
LOGIN:   POST /login  → bcrypt verify → session set → redirect home
LOGOUT:  POST /logout → session.clear() → redirect login

PROTECTED: every route checks request.session.get("user")
```

---

## 9. Request Flow

```
Browser: GET /
      ↓
FastAPI: check session → logged in?
      ↓ yes
PostgreSQL: SELECT movies (with filters)
      ↓
Jinja2: render home.html
      ↓
Browser: HTML page rendered
```

---

## 10. API Routes Reference

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | Yes | Home — movie grid |
| GET | `/login` | No | Login page |
| POST | `/login` | No | Process login |
| GET | `/signup` | No | Signup page |
| POST | `/signup` | No | Create account |
| POST | `/logout` | Yes | Logout |

---

## 11. How to Run

```bash
cd d:\OneDrive\Desktop\Postgres\movielens_app
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open: `http://localhost:8000`
