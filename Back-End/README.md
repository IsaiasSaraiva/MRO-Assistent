# MRO-Assistent

A RAG (Retrieval-Augmented Generation) chatbot for aviation maintenance technicians. Technicians upload PDF maintenance manuals and query them via natural language. The system retrieves relevant passages from the indexed manuals, generates answers using an LLM, and cites its sources.

Built as a university project and company prototype.

---

## Table of Contents

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Full Application](#running-the-full-application)
- [Demo Users](#demo-users)
- [Managing Users](#managing-users)
- [API Reference](#api-reference)
- [Important Notes](#important-notes)
- [Troubleshooting](#troubleshooting)

---

## Architecture

The application consists of two services that run side by side:

- **Backend** (Python/FastAPI) on `http://localhost:8000` -- handles authentication, PDF processing, vector storage, and LLM queries.
- **Frontend** (Next.js/React) on `http://localhost:3000` -- the user interface. Communicates with the backend over HTTP.

Each authenticated user has their own isolated ChromaDB collection. User A cannot see or query User B's documents.

---

## Tech Stack

**Backend:**
- Python 3.12
- FastAPI (REST API framework)
- ChromaDB (vector database, persistent, local)
- LangChain (orchestration)
- Groq API with llama-3.1-8b-instant (LLM inference)
- HuggingFace sentence-transformers/all-MiniLM-L6-v2 (embeddings, runs locally on CPU)
- PyMuPDF (PDF text extraction)
- pytesseract (OCR fallback for scanned PDFs)
- SQLite (user accounts and document metadata)
- JWT authentication (python-jose + bcrypt, 8-hour token expiry)

**Frontend:**
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui components

---

## Repository Structure

```
MRO-Assistent/                  <-- this repository (backend)
├── api.py                      FastAPI entrypoint
├── config.py                   All backend configuration
├── gerenciador_llm.py          LLMHandler (Groq API via langchain_groq)
├── processador_pdf.py          PDFProcessor (PyMuPDF + pytesseract OCR)
├── vector_store.py             VectorStoreManager (ChromaDB + HuggingFace embeddings)
├── create_user.py              Admin script to provision user accounts
├── api_contract.md             API endpoint reference
├── requirements.txt            Python dependencies (pinned)
├── .env                        Environment variables (not committed -- see setup)
├── routers/
│   ├── auth.py                 POST /auth/login
│   ├── documents.py            Upload, list, delete documents; clear collection
│   └── chat.py                 POST /chat (RAG query)
├── core/
│   ├── security.py             JWT creation, verification, get_current_user dependency
│   └── database.py             SQLite helpers (users and documents tables)
└── Assets/
    └── MRO.png                 Application logo

mro-frontend/                   <-- separate folder (frontend)
├── app/                        Next.js pages and layouts
├── components/
│   ├── layout/                 Header, Sidebar, AppShell
│   ├── documents/              DocumentList, UploadButton
│   └── chat/                   MessageBubble, SourceCard, ChatInput
├── lib/
│   ├── api.ts                  API client (all backend calls)
│   └── auth.ts                 JWT token helpers
├── proxy.ts                    Auth guard (redirects unauthenticated users to /login)
├── public/MRO.png              Logo
└── package.json                Node.js dependencies
```

---

## Prerequisites

Install these before proceeding:

| Requirement | Version | How to check |
|---|---|---|
| Python | 3.12 | `python3 --version` |
| Node.js | 18 or later | `node --version` |
| npm | 9 or later | `npm --version` |
| Git | any recent version | `git --version` |
| tesseract-ocr | 4.x or 5.x | `tesseract --version` |
| Groq API key | -- | Free at https://console.groq.com/keys |

### Installing tesseract-ocr

Tesseract is a system package required for OCR on scanned PDFs.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-por
```

**macOS (Homebrew):**
```bash
brew install tesseract
brew install tesseract-lang
```

**Windows:**
Download the installer from https://github.com/UB-Mannheim/tesseract/wiki and add it to your PATH. Install the English and Portuguese language packs during setup.

---

## Backend Setup

### 1. Clone the repository

```bash
git clone https://github.com/IsaiasSaraiva/MRO-Assistent.git
cd MRO-Assistent
```

### 2. Create and activate a virtual environment

**Linux / macOS:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the environment file

Create a file named `.env` in the project root with the following content:

```
GROQ_API_KEY=gsk_your_key_here
JWT_SECRET=mro-assistant-dev-secret-2025
```

Replace `gsk_your_key_here` with your actual Groq API key. Get one for free at https://console.groq.com/keys.

The `.env` file is listed in `.gitignore` and must never be committed to version control.

### 5. Provision demo users

```bash
python create_user.py
```

This creates a `users.db` SQLite database with 5 pre-configured accounts. The script is idempotent -- running it again will skip users that already exist.

### 6. Start the backend

```bash
uvicorn api:app --port 8000 --reload
```

The backend is now running at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

On first startup, the embedding model (sentence-transformers/all-MiniLM-L6-v2, approximately 90 MB) downloads automatically from HuggingFace. This happens once and is cached for subsequent runs.

---

## Frontend Setup

The frontend lives in a separate directory called `mro-frontend/` at the same level as the cloned repository.

### 1. Navigate to the frontend directory

```bash
cd mro-frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the development server

```bash
npm run dev
```

The frontend is now running at `http://localhost:3000`.

---

## Running the Full Application

Both services must be running simultaneously. Open two terminal windows:

**Terminal 1 -- Backend:**
```bash
cd MRO-Assistent
source venv/bin/activate
uvicorn api:app --port 8000 --reload
```

**Terminal 2 -- Frontend:**
```bash
cd mro-frontend
npm run dev
```

Open your browser at `http://localhost:3000`. You will see the login page.

---

## Demo Users

The following accounts are created by `create_user.py`:

| Name | Email | Password |
|---|---|---|
| Andre | andre.silva@mroassist.dev | Mro@Andre2025 |
| Fabio | fabio.costa@mroassist.dev | Mro@Fabio2025 |
| Rafael | rafael.mendes@mroassist.dev | Mro@Rafael2025 |
| Marcos | marcos.lima@mroassist.dev | Mro@Marcos2025 |
| Isaias | isaias.ferreira@mroassist.dev | Mro@Isaias2025 |

Each user has their own isolated document collection. Documents uploaded by one user are not visible to any other user.

---

## Managing Users

### Adding new users

Edit the `USERS` list in `create_user.py`, then run the script again:

```bash
python create_user.py
```

Existing users are skipped. Only new entries are inserted.

### Verifying users in the database

```bash
sqlite3 users.db "SELECT name, email FROM users;"
```

---

## API Reference

Full endpoint documentation is available at `http://localhost:8000/docs` when the backend is running. A static reference is in `api_contract.md`.

Summary of endpoints:

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | /auth/login | No | Authenticate and receive JWT |
| GET | /documents | Yes | List current user's indexed documents |
| POST | /documents/upload | Yes | Upload and process PDF files |
| DELETE | /documents/{id} | Yes | Remove a specific document |
| DELETE | /collection | Yes | Clear all of the current user's documents |
| POST | /chat | Yes | Ask a question (RAG query with sources) |
| GET | /health | No | Server liveness check |

All authenticated endpoints require an `Authorization: Bearer <token>` header.

---

## Important Notes

- **The `.env` file is gitignored.** It contains secrets (API key, JWT signing key) and must never be committed. Every developer creates their own `.env` locally.

- **Runtime data is gitignored.** The following are generated at runtime and excluded from version control: `venv/`, `chroma_db/`, `uploaded_pdfs/`, `users.db`.

- **The Groq API key is the developer's responsibility.** End users (technicians) never see or configure it. The key is loaded server-side and shared across all users. All requests count against one Groq account's rate limit.

- **The embedding model downloads on first run.** The all-MiniLM-L6-v2 model (~90 MB) is fetched from HuggingFace automatically and cached in the default HuggingFace cache directory (`~/.cache/huggingface/`). No manual download is needed.

- **OCR supports English and Portuguese.** The OCR fallback for scanned PDFs uses both language models (`eng+por`). Both tesseract language packs must be installed.

- **No hardcoded paths.** All file paths in the backend are derived from `config.BASE_DIR` (the directory where `config.py` lives) using `os.path.join`. The project runs on any machine regardless of the user's home directory or OS.

- **CORS is configured for local development.** The backend allows requests from `http://localhost:3000` and `http://127.0.0.1:3000`. If the frontend runs on a different port, update the `allow_origins` list in `api.py`.

---

## Troubleshooting

### "Address already in use" when starting the backend

Another process is using port 8000. Find and stop it:

```bash
lsof -ti:8000 | xargs kill
```

Then start the backend again.

### ChromaDB import error or sqlite3 compatibility issue

ChromaDB requires a recent version of SQLite. The `vector_store.py` file includes a compatibility patch that swaps `sqlite3` for `pysqlite3`. If you see SQLite-related errors, verify that `pysqlite3-binary` is installed:

```bash
pip install pysqlite3-binary
```

### OCR produces poor results

Verify the correct tesseract language packs are installed:

```bash
tesseract --list-langs
```

The output should include both `eng` and `por`. If either is missing, install the corresponding package (see the [Prerequisites](#prerequisites) section).

### Embedding model fails to download

If HuggingFace is unreachable or slow, the backend will hang or crash on first startup. Verify internet access and retry. Once downloaded, the model is cached and no further network access is needed.

### Frontend shows "Invalid credentials" for a correct password

Verify the users were provisioned:

```bash
sqlite3 users.db "SELECT email FROM users;"
```

If the table is empty, run `python create_user.py` again.
