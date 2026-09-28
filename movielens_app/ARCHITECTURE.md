# MovieLens App — High Level Architecture

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MOVIELENS APP                                │
│                                                                     │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│   │  Login   │    │   Home   │    │   Chat   │    │  Admin   │    │
│   │  Signup  │    │  Search  │    │   RAG    │    │   Dev    │    │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘    │
│                                                                     │
│                     FastAPI + Jinja2                                │
│                                                                     │
│   ┌─────────────────────┐         ┌─────────────────────────────┐  │
│   │     PostgreSQL      │         │         ChromaDB            │  │
│   │  movies, users,     │         │   PDF chunks (vectors)      │  │
│   │  ratings, history   │         │                             │  │
│   └─────────────────────┘         └─────────────────────────────┘  │
│                                                                     │
│                    ┌─────────────────┐                             │
│                    │  Ollama (Local) │                             │
│                    │  llama3.2:3b    │                             │
│                    └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Application Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                           │
│                                                                 │
│   base.html ──── navbar, bg-image, flow-bg.js                  │
│   auth.html ──── login / signup forms                          │
│   home.html ──── movie grid, search, stats                     │
│   chat.html ──── question form, answer, source chunks          │
│   admin.html ─── PDF upload form, indexed files list           │
│   dev.html ───── movie CRUD table, change history              │
│   chat_history.html ── past Q&A list                           │
│                                                                 │
│   style.css ──── dark theme, animations                        │
│   flow-bg.js ─── particle network background                   │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                               │
│                        main.py                                  │
│                                                                 │
│   GET  /              → home (movie search)                    │
│   GET  /login         → login page                             │
│   POST /login         → authenticate user                      │
│   GET  /signup        → signup page                            │
│   POST /signup        → create user                            │
│   POST /logout        → clear session                          │
│   GET  /chat          → chat page                              │
│   POST /chat          → RAG answer                             │
│   GET  /chat/history  → prompt history                         │
│   GET  /admin         → admin panel                            │
│   POST /admin/upload  → PDF upload + index                     │
│   GET  /dev           → dev panel                              │
│   POST /dev/add       → add movie                              │
│   POST /dev/edit      → edit movie                             │
│   POST /dev/delete    → delete movie                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│   DATA LAYER    │  │  RAG LAYER   │  │  LLM LAYER   │
│                 │  │              │  │              │
│  db.py          │  │ rag/         │  │ rag/llm.py   │
│  movie_db.py    │  │  ingest.py   │  │              │
│                 │  │  vector_     │  │  Ollama API  │
│  PostgreSQL     │  │  store.py    │  │  localhost   │
│                 │  │  pipeline.py │  │  :11434      │
│                 │  │              │  │              │
│                 │  │  ChromaDB    │  │  llama3.2:3b │
└─────────────────┘  └──────────────┘  └──────────────┘
```

---

## 3. Authentication Flow

```
User visits any page
        │
        ▼
   Logged in? ──── NO ──→ Redirect to /login
        │
       YES
        │
        ▼
   Role check
   ┌─────┴──────┐
   │            │
  user        admin
   │            │
   ▼            ▼
 Home        Home
 Chat        Chat
 History     History
             Admin Panel  (/admin)
             Dev Panel    (/dev)


LOGIN FLOW:
──────────
POST /login
    │
    ▼
users table → email match?
    │
    ▼
bcrypt.checkpw(password, hash)
    │
    ▼
Session → { id, name, role }
    │
    ▼
Redirect → /
```

---

## 4. RAG Pipeline Flow

```
                    USER QUESTION
                         │
                         ▼
              ┌─────────────────────┐
              │   rag/pipeline.py   │
              │   answer_question() │
              └──────────┬──────────┘
                         │
           ┌─────────────┴──────────────┐
           │                            │
           ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐
│  VECTOR SEARCH      │      │   SQL CONTEXT       │
│                     │      │                     │
│ Question            │      │ movie_db.py         │
│     ↓               │      │     ↓               │
│ SentenceTransformer │      │ PostgreSQL          │
│ (embedding)         │      │ movies + ratings    │
│     ↓               │      │     ↓               │
│ ChromaDB search     │      │ Top rated / search  │
│     ↓               │      │ by title            │
│ Top 3 similar chunks│      │     ↓               │
│ from PDF            │      │ Structured text     │
└──────────┬──────────┘      └──────────┬──────────┘
           │                            │
           └─────────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   PROMPT BUILDER    │
              │                     │
              │ Context (PDF chunks)│
              │ + SQL data          │
              │ + User question     │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   rag/llm.py        │
              │                     │
              │ Ollama HTTP POST    │
              │ localhost:11434     │
              │ model: llama3.2:3b  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   SAVE HISTORY      │
              │                     │
              │ db.py               │
              │ rag_prompt_history  │
              │ (PostgreSQL)        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   RESPONSE          │
              │                     │
              │ Answer text         │
              │ Source chunks       │
              │ → chat.html         │
              └─────────────────────┘
```

---

## 5. PDF Ingestion Flow

```
Admin uploads PDF
        │
        ▼
POST /admin/upload
        │
        ▼
Save to static/uploads/
        │
        ▼
rag/ingest.py → ingest_pdf()
        │
        ▼
pymupdf → extract all text from PDF
        │
        ▼
Split into chunks
  chunk_size  = 500 chars
  overlap     = 50 chars
        │
        ▼
rag/vector_store.py → add_documents()
        │
        ▼
SentenceTransformer
  model: all-MiniLM-L6-v2
  each chunk → 384-dim vector
        │
        ▼
ChromaDB PersistentClient
  stored in: ./chroma_db/
        │
        ▼
✅ Indexed — ready for search
```

---

## 6. Movie Management Flow (Dev Panel)

```
                    ADMIN → /dev
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       ADD            EDIT           DELETE
          │              │              │
          ▼              ▼              ▼
  INSERT INTO      Save old values   Save to
  movies           to movie_history  movie_history
  (title, genres)  (BEFORE_EDIT)     (DELETED)
          │              │              │
          ▼              ▼              ▼
  movie_history    UPDATE movies     DELETE FROM
  (ADDED)          (new values)      movies
                         │
                         ▼
                   movie_history
                   (EDITED)

RESULT:
  User searches → updated data instantly ✅
  History table → full audit trail ✅
  Old values → recoverable from history ✅
```

---

## 7. Database Schema

```
PostgreSQL (movie_db)
│
├── movies
│   ├── movie_id    SERIAL PRIMARY KEY
│   ├── title       TEXT
│   └── genres      TEXT  (pipe separated: Action|Drama)
│
├── ratings
│   ├── user_id     INTEGER
│   ├── movie_id    INTEGER → movies.movie_id
│   ├── rating      FLOAT
│   └── timestamp   BIGINT
│
├── users
│   ├── id          SERIAL PRIMARY KEY
│   ├── name        TEXT
│   ├── email       TEXT UNIQUE
│   ├── password_hash TEXT
│   ├── role        TEXT  (user / admin)
│   └── created_at  TIMESTAMP
│
├── movie_history
│   ├── id          SERIAL PRIMARY KEY
│   ├── movie_id    INTEGER
│   ├── title       TEXT
│   ├── genres      TEXT
│   ├── action      TEXT  (ADDED/EDITED/BEFORE_EDIT/DELETED)
│   ├── changed_by  TEXT
│   └── changed_at  TIMESTAMP
│
├── rag_prompt_history
│   ├── history_id  BIGSERIAL PRIMARY KEY
│   ├── user_prompt TEXT
│   ├── response    TEXT
│   ├── retrieved_sources TEXT
│   ├── sql_context TEXT
│   └── created_at  TIMESTAMP
│
└── prompt_history
    ├── id          SERIAL PRIMARY KEY
    ├── user_id     INTEGER → users.id
    ├── question    TEXT
    ├── answer      TEXT
    ├── sources     TEXT
    └── created_at  TIMESTAMP


ChromaDB (./chroma_db/)
│
└── collection: documents
    ├── id          chunk_0, chunk_1, ...
    ├── text        500 char chunk from PDF
    └── embedding   384-dim float vector
```

---

## 8. Tech Stack Summary

```
┌─────────────────────────────────────────────────────┐
│                   TECH STACK                        │
├─────────────────┬───────────────────────────────────┤
│ Backend         │ FastAPI, Uvicorn, Starlette        │
├─────────────────┼───────────────────────────────────┤
│ Database        │ PostgreSQL (psycopg3)              │
├─────────────────┼───────────────────────────────────┤
│ Vector DB       │ ChromaDB (local persistent)        │
├─────────────────┼───────────────────────────────────┤
│ Embeddings      │ SentenceTransformer all-MiniLM-L6  │
├─────────────────┼───────────────────────────────────┤
│ LLM             │ Ollama llama3.2:3b (local)         │
├─────────────────┼───────────────────────────────────┤
│ PDF Parsing     │ pymupdf (fitz)                     │
├─────────────────┼───────────────────────────────────┤
│ Auth            │ bcrypt + SessionMiddleware         │
├─────────────────┼───────────────────────────────────┤
│ Frontend        │ Jinja2, Vanilla CSS, Vanilla JS    │
├─────────────────┼───────────────────────────────────┤
│ Config          │ python-dotenv (.env)               │
├─────────────────┼───────────────────────────────────┤
│ HTTP Client     │ requests (Ollama API call)         │
├─────────────────┼───────────────────────────────────┤
│ Python Stdlib   │ os, re, json, hashlib, pathlib     │
├─────────────────┼───────────────────────────────────┤
│ Unused (in req) │ passlib, ollama (Python lib)       │
└─────────────────┴───────────────────────────────────┘
```

---

## 10. Python Stdlib Usage

```
┌─────────────┬────────────────────────────────────────────┐
│ Module      │ Used For                                   │
├─────────────┼────────────────────────────────────────────┤
│ os          │ File paths, env vars, listdir              │
├─────────────┼────────────────────────────────────────────┤
│ re          │ Extract movie title from user question     │
│             │ (movie_db.py regex patterns)               │
├─────────────┼────────────────────────────────────────────┤
│ json        │ Serialize sources list for DB storage      │
├─────────────┼────────────────────────────────────────────┤
│ hashlib     │ SHA1 unique IDs for ChromaDB chunks        │
├─────────────┼────────────────────────────────────────────┤
│ pathlib     │ Create chroma_db/ directory if missing     │
└─────────────┴────────────────────────────────────────────┘
```

---

## 11. External HTTP Calls

```
rag/llm.py
    │
    ▼
requests.post(
    url   = http://localhost:11434/api/generate
    json  = { model, prompt, stream:false }
    timeout = 120s
)
    │
    ▼
Ollama local server
    │
    ▼
llama3.2:3b model
    │
    ▼
JSON response → data["response"]

Note: No external internet calls.
      Everything runs 100% locally.
```

---

## 9. Folder Structure

```
movielens_app/
│
├── main.py              ← All routes (FastAPI)
├── db.py                ← PostgreSQL connection + RAG history
├── movie_db.py          ← SQL context for RAG
│
├── rag/
│   ├── ingest.py        ← PDF → chunks
│   ├── vector_store.py  ← ChromaDB operations
│   ├── llm.py           ← Ollama API call
│   └── pipeline.py      ← Full RAG orchestration
│
├── templates/
│   ├── base.html        ← Navbar, background
│   ├── auth.html        ← Login / Signup
│   ├── home.html        ← Movie search grid
│   ├── chat.html        ← RAG chat interface
│   ├── chat_history.html← Past Q&A
│   ├── admin.html       ← PDF upload
│   └── dev.html         ← Movie CRUD + history
│
├── static/
│   ├── css/style.css    ← Dark theme styles
│   ├── js/flow-bg.js    ← Background animation
│   ├── movie_image.jpg  ← Background image
│   └── uploads/         ← Uploaded PDFs
│
├── chroma_db/           ← ChromaDB vector storage
├── .env                 ← DB creds, Ollama config
└── requirements.txt     ← Python dependencies
```
