# StudyMate AI — Master Build Prompt

You are the senior software engineer responsible for building **StudyMate AI**, a professional, modular, offline-first Python study assistant.

This document is the authoritative implementation brief. Build the project incrementally, verify every phase before moving on, and do not invent requirements that are not specified here.

---

## 1. Product Definition

### Project
**StudyMate AI**

### Goal
Build an offline AI-powered study assistant that turns a student's collection of PDFs, PowerPoint files, Word documents, scanned notes, and question papers into a searchable personal knowledge base.

The system should let a student:

- upload and organize study materials
- extract text from supported documents
- OCR scanned/image-based documents
- store document/page metadata
- search across all study materials
- perform semantic search using embeddings
- ask questions using Retrieval-Augmented Generation (RAG)
- generate summaries
- generate flashcards
- generate quizzes
- create revision notes
- inspect which source documents/pages support an answer
- use local/offline AI by default, with cloud AI treated as an optional integration

The application must be designed as a real software product rather than a single Streamlit script.

---

## 2. Non-Negotiable Engineering Principles

Use the coding principles from the supplied Karpathy-inspired guidelines:

1. **Think before coding**
   - Inspect the existing project before changing it.
   - State assumptions when requirements are ambiguous.
   - Do not silently choose between materially different implementations.
   - Prefer the simplest viable solution.

2. **Simplicity first**
   - Implement only requested functionality.
   - Avoid speculative abstractions.
   - Do not introduce unnecessary frameworks, services, queues, microservices, or configuration systems.
   - A small working implementation is preferable to a large theoretical architecture.

3. **Surgical changes**
   - When modifying existing code, change only what the task requires.
   - Do not perform unrelated refactoring.
   - Preserve existing conventions unless there is a concrete reason to change them.
   - Remove only unused code introduced by your own changes.

4. **Goal-driven execution**
   - Every phase must have explicit acceptance criteria.
   - Write tests for important behavior.
   - Verify each phase before proceeding.
   - If a task fails, diagnose the failure before adding more code.

The supplied guidelines explicitly emphasize surfacing assumptions, avoiding speculative complexity, making surgical changes, and defining verifiable success criteria. Apply those principles throughout the project.

---

## 3. Product Constraints

### Required stack

- Python 3.12+
- Streamlit frontend
- SQLite database
- Modular Python backend
- Local/offline-first processing
- Embeddings for semantic search
- RAG pipeline for question answering

### Suggested libraries

Use these only where they solve an actual requirement:

- `streamlit` — UI
- `sqlalchemy` — database access
- `pydantic` — validation/configuration where useful
- `pymupdf` or `pypdf` — PDF extraction
- `python-pptx` — PowerPoint extraction
- `python-docx` — Word extraction
- `Pillow` — image processing
- `pytesseract` — OCR
- `sentence-transformers` — local embeddings
- `faiss-cpu` or a similarly simple local vector index — semantic retrieval
- `numpy` — vector operations
- `ollama` Python client or HTTP interface — optional local LLM
- `pytest` — testing

Do not install every suggested dependency at the beginning. Add dependencies phase-by-phase when they are required.

---

# 4. High-Level Architecture

Use a layered modular architecture:

```text
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI                      │
│ Dashboard | Upload | Search | Chat | Study Tools   │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                 Application Layer                    │
│ Document Service | Search Service | RAG Service     │
│ Summary Service | Flashcard Service | Quiz Service  │
└───────────────┬───────────────────────┬──────────────┘
                │                       │
┌───────────────▼──────────────┐ ┌─────▼──────────────┐
│      Processing Layer        │ │    AI Layer         │
│ Parsers | OCR | Chunking     │ │ Embeddings | LLM    │
└───────────────┬──────────────┘ └─────┬──────────────┘
                │                      │
                └──────────┬───────────┘
                           │
              ┌────────────▼────────────┐
              │     Persistence Layer   │
              │ SQLite | Vector Index   │
              │ File Storage            │
              └─────────────────────────┘
```

### Data flow

```text
Upload
  ↓
File validation
  ↓
Document metadata creation
  ↓
Format-specific text extraction
  ↓
OCR fallback when required
  ↓
Page normalization
  ↓
Text chunking
  ↓
Embedding generation
  ↓
Vector index
  ↓
SQLite metadata/storage
  ↓
Search / RAG / Study Tools
```

---

# 5. Required Project Architecture

Create this structure:

```text
studymate-ai/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── agent.md
├── skills.md
│
├── data/
│   ├── uploads/
│   ├── processed/
│   ├── vectors/
│   └── studymate.db
│
├── src/
│   └── studymate/
│       ├── __init__.py
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── models.py
│       │   └── repositories.py
│       │
│       ├── documents/
│       │   ├── __init__.py
│       │   ├── manager.py
│       │   ├── validators.py
│       │   ├── metadata.py
│       │   └── parsers/
│       │       ├── __init__.py
│       │       ├── base.py
│       │       ├── pdf.py
│       │       ├── docx.py
│       │       ├── pptx.py
│       │       └── image.py
│       │
│       ├── ocr/
│       │   ├── __init__.py
│       │   └── service.py
│       │
│       ├── text/
│       │   ├── __init__.py
│       │   ├── cleaner.py
│       │   ├── chunker.py
│       │   └── models.py
│       │
│       ├── embeddings/
│       │   ├── __init__.py
│       │   └── service.py
│       │
│       ├── search/
│       │   ├── __init__.py
│       │   ├── keyword.py
│       │   ├── semantic.py
│       │   └── hybrid.py
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── retriever.py
│       │   ├── prompt.py
│       │   └── service.py
│       │
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── llm.py
│       │   └── local.py
│       │
│       ├── study/
│       │   ├── __init__.py
│       │   ├── summaries.py
│       │   ├── flashcards.py
│       │   ├── quizzes.py
│       │   └── revision.py
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── dashboard.py
│       │   ├── upload.py
│       │   ├── search.py
│       │   ├── chat.py
│       │   └── study_tools.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logging.py
│           └── files.py
│
└── tests/
    ├── conftest.py
    ├── test_documents.py
    ├── test_parsers.py
    ├── test_chunking.py
    ├── test_search.py
    ├── test_rag.py
    └── test_study_tools.py
```

Do not create all modules as empty placeholders unless the phase requires them. Build the architecture progressively.

---

# 6. Database Design

Use SQLite.

Minimum required entities:

## documents

```text
id
filename
filepath
file_size
file_type
pages
author
upload_date
status
error_message
```

## pages

```text
id
document_id
page_number
extracted_text
ocr_used
```

Add a foreign key from `pages.document_id` to `documents.id`.

## chunks

Required for semantic retrieval:

```text
id
page_id
chunk_index
text
```

## embeddings/index metadata

Do not store large embedding vectors directly in SQLite unless there is a concrete reason to do so.

Use a local vector index and persist the mapping between vector IDs and chunk IDs.

Keep database responsibilities separate from vector-index responsibilities.

---

# 7. Core Functional Requirements

## Phase 1 — Project foundation

Implement:

- project structure
- configuration
- SQLite initialization
- SQLAlchemy models/repositories
- logging
- Streamlit entry point
- basic dashboard

### Verify

- application starts
- database is created
- tables are created
- Streamlit dashboard renders
- no unnecessary AI dependencies are required yet

---

## Phase 2 — Document ingestion

Support:

- PDF
- DOCX
- PPTX
- common image files

Pipeline:

```text
Upload
→ validate extension
→ save original file
→ create document record
→ select parser
→ extract pages
→ save pages
→ update document status
```

### Requirements

- preserve page boundaries where possible
- store extracted text per page
- report extraction errors clearly
- avoid silently losing files
- prevent unsupported formats from entering the pipeline

### Verify

Test at least:

- text PDF
- DOCX
- PPTX
- image
- unsupported extension
- empty/corrupt file

---

## Phase 3 — OCR

For image-based/scanned material:

```text
Page/image
→ image preprocessing if necessary
→ OCR
→ normalized text
→ page record
```

OCR must be a fallback or explicit processing path rather than blindly running OCR over every text-based page.

Store whether OCR was used.

### Verify

- scanned document produces searchable text
- normal text PDF does not unnecessarily require OCR
- OCR failure is reported rather than silently producing empty text

---

## Phase 4 — Text processing

Implement:

- whitespace cleanup
- repeated-header/footer handling where reliably detectable
- Unicode normalization where appropriate
- chunking

Chunking must preserve source metadata:

```text
chunk
→ document_id
→ page_id
→ page_number
→ chunk_index
→ text
```

Start with a simple deterministic chunking strategy.

Do not build a complicated adaptive chunking framework unless testing proves it is needed.

### Verify

- no empty chunks
- chunks remain traceable to pages
- chunk sizes remain within configured limits
- repeated processing produces deterministic output

---

## Phase 5 — Semantic search

Implement local embeddings.

Pipeline:

```text
chunks
→ embedding model
→ vectors
→ local vector index
```

Search:

```text
query
→ query embedding
→ nearest-neighbor search
→ chunk IDs
→ source metadata
```

Every search result must show:

- document name
- page number
- relevant text
- similarity/relevance score

### Verify

Create a small test corpus where the expected semantic result is known.

Test:

- exact keyword search
- semantic query
- top-k retrieval
- source/page mapping
- empty corpus
- malformed index recovery

---

# 8. Hybrid Search

Implement both:

1. keyword search
2. semantic search

Then provide a simple hybrid strategy.

Do not overengineer ranking.

The initial hybrid approach may combine normalized keyword and semantic scores.

Keep the scoring logic isolated so it can be tested independently.

---

# 9. RAG Question Answering

Implement:

```text
User question
      ↓
query preprocessing
      ↓
retrieval
      ↓
top-k chunks
      ↓
context construction
      ↓
local LLM
      ↓
answer
      ↓
source citations
```

The model must be instructed:

- answer only from retrieved study material when the question is document-grounded
- do not fabricate unsupported facts
- clearly state when the material does not contain enough information
- cite source document and page for claims when possible

The UI should expose the retrieved sources.

### Offline requirement

The default design must support a local model through Ollama or an equivalent local runtime.

Cloud LLM providers may be added as optional adapters later, but they must not be required for the core product.

---

# 10. Study Tools

Build the following on top of retrieved document content.

## Summaries

Support:

- document summary
- page/section summary
- selected text summary

## Flashcards

Generate:

```text
question
answer
source_document
source_page
```

Allow the user to review cards.

## Quizzes

Generate questions from selected study material.

Support at minimum:

- multiple choice
- answer
- explanation
- source

## Revision notes

Generate concise structured notes from selected material.

All AI-generated study content should preserve source references where practical.

---

# 11. Streamlit UI

Create a professional, simple dashboard.

Recommended navigation:

```text
StudyMate AI
├── Dashboard
├── My Materials
├── Upload
├── Search
├── AI Chat
└── Study Tools
    ├── Summarize
    ├── Flashcards
    ├── Quiz
    └── Revision Notes
```

Dashboard should show useful metrics such as:

- total documents
- total pages
- total chunks
- recently added material
- indexing status

Do not make the UI visually complicated before the backend works.

---

# 12. Document Processing State

Use explicit processing states, for example:

```text
uploaded
processing
processed
indexed
failed
```

The exact enum/string implementation can be chosen during implementation.

The UI must make failures visible.

---

# 13. Configuration

Centralize only necessary configuration:

```text
DATABASE_PATH
UPLOAD_DIR
VECTOR_DIR
EMBEDDING_MODEL
LLM_PROVIDER
LLM_MODEL
CHUNK_SIZE
CHUNK_OVERLAP
TOP_K
OCR_ENABLED
```

Provide `.env.example`.

Do not create a large configuration framework.

---

# 14. Error Handling

Handle realistic failures:

- unsupported files
- corrupt files
- parser errors
- OCR unavailable
- embedding model unavailable
- vector index missing/corrupt
- local LLM unavailable
- database errors

Errors should be:

- logged
- understandable to developers
- converted into useful UI messages where appropriate

Do not catch broad exceptions everywhere. Handle failures at meaningful boundaries.

---

# 15. Testing Strategy

Use pytest.

Minimum tests:

### Database

- document creation
- page relationship
- chunk relationship

### Parsers

- PDF extraction
- DOCX extraction
- PPTX extraction
- image/OCR path

### Text

- cleaning
- chunking
- deterministic output

### Search

- keyword retrieval
- semantic retrieval
- hybrid ranking
- source mapping

### RAG

- context construction
- source attribution
- no-context behavior

### Study tools

- summary output structure
- flashcard structure
- quiz structure

Tests should avoid requiring a live cloud API.

For local AI components, use mocks/fakes in unit tests.

---

# 16. Implementation Order

Do not attempt to implement the entire application in one pass.

Use this order:

```text
1. Inspect repository
2. Establish project structure
3. Configuration + logging
4. SQLite + models
5. Streamlit shell
6. File upload
7. Document parsers
8. OCR
9. Text cleaning
10. Chunking
11. Embeddings
12. Vector index
13. Keyword search
14. Semantic search
15. Hybrid search
16. RAG
17. Local LLM adapter
18. Summaries
19. Flashcards
20. Quizzes
21. Revision notes
22. Dashboard analytics
23. Integration tests
24. Documentation
25. Final verification
```

After each major step:

```text
Implement
→ run tests
→ run application/manual check
→ inspect errors
→ fix only relevant issues
→ continue
```

---

# 17. Definition of Done

The project is complete only when:

- Streamlit starts successfully
- a user can upload supported documents
- document metadata is persisted
- page-level text is persisted
- scanned content can be OCR'd
- documents are chunked
- chunks are embedded locally
- semantic search returns relevant sources
- hybrid search works
- RAG answers questions from retrieved content
- answers expose source documents/pages
- summaries work
- flashcards work
- quizzes work
- revision notes work
- the application remains usable without a cloud API
- important failure paths are handled
- automated tests pass
- README explains setup and usage
- no unnecessary speculative architecture remains

---

# 18. Agent Behavior

Before every implementation task:

1. inspect relevant files
2. identify the smallest change
3. state assumptions if necessary
4. define verification
5. implement
6. test
7. report what changed and what was verified

If requirements conflict:

- stop
- identify the conflict
- explain the tradeoff
- ask for clarification if the decision materially affects architecture

Never silently introduce:

- authentication
- cloud databases
- Docker
- Redis
- Celery
- Kubernetes
- microservices
- paid APIs
- complex plugin systems
- unnecessary design patterns

unless explicitly requested or demonstrably required.

---

# 19. Final Developer Instruction

Treat StudyMate AI as a real product, but build it incrementally.

Prioritize:

**correctness → simplicity → traceability → testability → UX polish**

Do not optimize prematurely.

Do not claim a feature works until it has been verified.

When a simpler implementation satisfies the requirement, use the simpler implementation.
