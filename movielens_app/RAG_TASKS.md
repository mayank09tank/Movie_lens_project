# RAG Integration — Architecture & Task Plan

## 7 Tasks

```
T1 → Admin should be able to upload files (PDF)
T2 → Read PDF file and vectorize data
T3 → Use Vector DB
T4 → Use a Model to train on the data (Local LLM)
T5 → Create a Page for user prompt
T6 → Maintain Prompt History
T7 → Show the response from the RAG
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ADMIN FLOW                           │
│                                                             │
│   Admin Login                                               │
│       ↓                                                     │
│   T1: /admin → Upload PDF                                   │
│       ↓                                                     │
│   T2: ingest.py                                             │
│       → Read PDF (PyMuPDF)                                  │
│       → Split into chunks (500 chars, 50 overlap)           │
│       → Generate Embeddings (sentence-transformers)         │
│       ↓                                                     │
│   T3: ChromaDB → Store chunks + embeddings                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        USER FLOW                            │
│                                                             │
│   User Login                                                │
│       ↓                                                     │
│   T5: /chat → User types question                           │
│       ↓                                                     │
│   T3: ChromaDB → Find top 3 similar chunks                  │
│       ↓                                                     │
│   T4: Ollama llama3 → question + chunks → Answer            │
│       ↓                                                     │
│   T6: PostgreSQL → Save question + answer to history        │
│       ↓                                                     │
│   T7: chat.html → Show answer + source chunks               │
│       ↓                                                     │
│   T6: /chat/history → View all past prompts                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure (after integration)

```
movielens_app/
│
├── main.py                      ← add new routes (T1, T5, T6, T7)
│
├── rag/
│   ├── __init__.py
│   ├── ingest.py                ← T2: read PDF + chunk + embed
│   ├── vector_store.py          ← T3: ChromaDB store + query
│   └── llm.py                   ← T4: Ollama llama3
│
├── static/
│   ├── css/style.css
│   └── uploads/                 ← T1: PDFs saved here
│
└── templates/
    ├── base.html
    ├── auth.html
    ├── home.html
    ├── admin.html               ← T1: upload form
    ├── chat.html                ← T5 + T7: prompt + answer
    └── chat_history.html        ← T6: history page
```

---

## Task Details

### T1 — Admin Upload PDF
```
GET  /admin        → show upload form
POST /admin/upload → save PDF → trigger T2
Access: admin role only
```

### T2 — Read PDF + Vectorize
```
File:    rag/ingest.py
Library: PyMuPDF (fitz)
Steps:
  1. fitz.open(pdf) → extract text
  2. split into 500 char chunks
  3. sentence-transformers → embeddings
  4. send to ChromaDB (T3)
```

### T3 — Vector DB
```
File:       rag/vector_store.py
Library:    chromadb
Collection: movielens_docs
add_documents(chunks) → store
query(question, top_k=3) → retrieve
```

### T4 — Local LLM
```
File:   rag/llm.py
Tool:   Ollama (local)
Model:  llama3
Input:  question + top 3 chunks
Output: answer string
```

### T5 — User Prompt Page
```
GET  /chat → prompt input page
POST /chat → run RAG → show answer
Template: chat.html
```

### T6 — Prompt History
```
Table: prompt_history
  (id, user_id, question, answer, sources, created_at)

GET /chat/history → show all past Q&A
```

### T7 — RAG Response
```
POST /chat flow:
  1. ChromaDB → top 3 chunks
  2. Ollama   → generate answer
  3. Show on chat.html
  4. Save to prompt_history
```

---

## New DB Table

```sql
CREATE TABLE prompt_history (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id),
    question   TEXT NOT NULL,
    answer     TEXT NOT NULL,
    sources    TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Dependencies

```bash
pip install pymupdf sentence-transformers chromadb ollama
```

```bash
# Ollama: https://ollama.com
ollama pull llama3
ollama serve
```

---

## New Routes

| Method | Route | Who | Task |
|--------|-------|-----|------|
| GET | `/admin` | Admin | T1 |
| POST | `/admin/upload` | Admin | T1 + T2 |
| GET | `/chat` | User | T5 |
| POST | `/chat` | User | T3+T4+T7 |
| GET | `/chat/history` | User | T6 |
