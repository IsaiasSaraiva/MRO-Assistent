# MRO Assistant API Contract

**Base URL:** `http://localhost:8000`
**Auth:** Bearer JWT token (obtained via `/auth/login`, passed in `Authorization: Bearer <token>` header)

---

## Authentication

### POST /auth/login

Authenticate a user and receive a JWT access token.

**Request body (JSON):**
```json
{
  "email": "andre.silva@mroassist.dev",
  "password": "Mro@Andre2025"
}
```

**Response 200:**
```json
{
  "access_token": "<jwt_string>",
  "token_type": "bearer",
  "user_name": "Andre"
}
```

**Response 401:** Invalid credentials.

---

## Documents

All document endpoints require `Authorization: Bearer <token>`.

### GET /documents

List all documents uploaded by the authenticated user.

**Response 200:**
```json
[
  {
    "id": "uuid-string",
    "filename": "manual.pdf",
    "chunk_count": 42,
    "uploaded_at": "2025-01-01 12:00:00"
  }
]
```

Returns `[]` if no documents uploaded yet.

---

### POST /documents/upload

Upload one or more PDF files. Multipart form data.

**Request:** `multipart/form-data` with field `files` (one or multiple PDF files).

**Response 200:**
```json
[
  {
    "filename": "manual.pdf",
    "num_chunks": 42,
    "status": "success"
  },
  {
    "filename": "duplicate.pdf",
    "num_chunks": 0,
    "status": "duplicate"
  }
]
```

- `status: "success"` — file processed and stored.
- `status: "duplicate"` — file with same content hash already exists for this user; skipped.

---

### DELETE /documents/{document_id}

Delete a specific document by its UUID, including its vector embeddings.

**Path parameter:** `document_id` — UUID of the document to delete.

**Response 200:**
```json
{ "success": true }
```

**Response 404:** Document not found or does not belong to the authenticated user.

---

## Chat

### POST /chat

Ask a question against the authenticated user's uploaded documents (RAG).

**Request body (JSON):**
```json
{
  "question": "Qual o procedimento para troca de filtro de óleo?"
}
```

**Response 200:**
```json
{
  "answer": "O procedimento para troca de filtro de óleo é...",
  "sources": [
    {
      "filename": "manual_manutencao.pdf",
      "page": 12,
      "excerpt": "Primeiro, drene o óleo residual..."
    }
  ]
}
```

- `sources` — up to 3 most relevant chunks retrieved from ChromaDB.
- If no documents are uploaded, `answer` will indicate so and `sources` will be `[]`.

---

## Collection Management

### DELETE /collection

Delete the entire ChromaDB collection and all document records for the authenticated user. Use with caution — this is irreversible.

**Response 200:**
```json
{ "success": true }
```

---

## Health

### GET /health

Check API liveness. No authentication required.

**Response 200:**
```json
{ "status": "ok" }
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200  | Success |
| 401  | Unauthorized (missing, invalid, or expired token) |
| 404  | Resource not found or access denied |
| 422  | Validation error (malformed request body) |
| 500  | Internal server error |

---

## Notes

- JWT tokens expire after 8 hours.
- Each user has an isolated ChromaDB collection (`user_<id>_docs`).
- File deduplication is based on SHA-256 hash of file contents, scoped per user.
- Chat does not use conversation history (stateless per request).
- OCR is applied automatically to scanned PDFs (Portuguese language, `por`).
