# agent.md — StudyMate AI Development Agent

## Mission

You are the primary coding agent for **StudyMate AI**.

Your responsibility is to build a maintainable, offline-first study assistant that converts student documents into a searchable knowledge base and provides grounded AI study tools.

The product must be implemented incrementally. Do not attempt to build the entire system in one uncontrolled pass.

---

# 1. Project Goals

## Primary goal

Create a working local application that allows a student to:

1. upload study material
2. extract text
3. OCR scanned material
4. organize documents/pages/chunks
5. search using keywords
6. search semantically using embeddings
7. ask questions using RAG
8. generate summaries
9. generate flashcards
10. generate quizzes
11. generate revision notes

## Engineering goals

The project must be:

- modular
- understandable
- testable
- offline-first
- source-traceable
- simple enough for a student developer to maintain
- extensible without speculative architecture

---

# 2. Source of Truth

Use these requirements as the implementation source of truth:

- StudyMate AI project brief supplied by the user
- this agent.md
- skills.md
- existing repository code
- explicit user instructions

When existing code and a requirement conflict, do not silently rewrite the project. Explain the conflict and make the smallest justified change.

---

# 3. Operating Principles

## Think Before Coding

Before implementation:

1. inspect the relevant code
2. identify assumptions
3. identify dependencies
4. identify the smallest solution
5. define how success will be verified

If a material ambiguity affects architecture or behavior, ask before implementing.

## Simplicity First

Use the minimum architecture needed.

Do not add a feature because it might be useful later.

Do not build:

- microservices
- Redis
- Celery
- Kubernetes
- cloud databases
- authentication
- complex plugin systems

unless explicitly required.

## Surgical Changes

Only modify what the current task requires.

Do not:

- reformat unrelated files
- rename unrelated variables
- rewrite working modules
- perform drive-by refactoring
- delete pre-existing code without instruction

## Goal-Driven Execution

Every task must have a measurable result.

Bad:

```text
Improve search.
```

Good:

```text
Implement semantic search over indexed chunks.

Verification:
- index can be loaded
- query returns top-k chunks
- returned chunks map to valid pages
- relevant semantic test passes
```

---

# 4. Architecture

Use:

```text
Streamlit UI
      ↓
Application Services
      ↓
Processing / Domain Services
      ↓
SQLite + File Storage + Vector Index + Local AI
```

Recommended structure:

```text
studymate-ai/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
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
│       ├── config/
│       ├── db/
│       ├── documents/
│       │   └── parsers/
│       ├── ocr/
│       ├── text/
│       ├── embeddings/
│       ├── search/
│       ├── rag/
│       ├── ai/
│       ├── study/
│       ├── ui/
│       └── utils/
│
└── tests/
```

Keep responsibilities separate.

---

# 5. Core Data Model

## Document

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

## Page

```text
id
document_id
page_number
extracted_text
ocr_used
```

## Chunk

```text
id
page_id
chunk_index
text
```

Relationship:

```text
Document 1 ─── N Pages
Page     1 ─── N Chunks
```

Vector IDs must map back to chunk IDs.

---

# 6. Development Roadmap

## Task 0 — Repository audit

### Work

- inspect repository
- inspect existing files
- inspect dependencies
- inspect tests
- identify current entry point

### Success

A short architecture assessment exists and no code is changed unnecessarily.

---

## Task 1 — Foundation

### Build

- package structure
- settings
- logging
- SQLite initialization
- models
- basic Streamlit shell

### Verify

```text
streamlit run app.py
```

must launch.

Database tables must exist.

---

## Task 2 — Upload system

### Build

- Streamlit upload UI
- file validation
- local file storage
- document record

### Verify

Uploading a supported file creates:

```text
original file
+
document database record
```

Unsupported files are rejected cleanly.

---

## Task 3 — Parsers

### Build

PDF, DOCX, PPTX and image parsing.

Use a common parser contract only if it genuinely simplifies the implementation.

### Verify

Each parser has a focused test.

---

## Task 4 — OCR

### Build

OCR for scanned/image-based content.

### Verify

A scanned sample becomes searchable text.

Normal text documents do not unnecessarily pass through OCR.

---

## Task 5 — Text processing

### Build

- cleaner
- chunker
- chunk metadata

### Verify

- no empty chunks
- deterministic output
- source/page traceability

---

## Task 6 — Embeddings

### Build

Local embedding service and persisted vector index.

### Verify

- embeddings can be generated
- index persists
- index reloads
- vector IDs map to valid chunks

---

## Task 7 — Search

### Build

1. keyword search
2. semantic search
3. hybrid search

### Verify

Search returns:

```text
document
page
text
score
```

---

## Task 8 — RAG

### Build

Retriever + context builder + local LLM adapter + source attribution.

### Verify

Given a known document:

```text
question
→ relevant chunks
→ grounded answer
→ source/page references
```

If the required information is absent, the system should not fabricate an answer.

---

## Task 9 — Summaries

### Build

- document summary
- selected material summary

### Verify

Generated summary uses selected/retrieved context.

---

## Task 10 — Flashcards

### Build

Flashcard generation and review UI.

### Verify

Each card contains:

```text
question
answer
source
```

---

## Task 11 — Quizzes

### Build

MCQ generation and answer/explanation flow.

### Verify

Each quiz question has:

```text
question
options
correct answer
explanation
source
```

---

## Task 12 — Revision notes

### Build

Generate concise structured revision notes.

### Verify

Notes are generated from selected source material.

---

## Task 13 — Dashboard

### Build

Show:

- document count
- page count
- chunk count
- recent documents
- processing/indexing status

### Verify

Dashboard values match database state.

---

## Task 14 — Integration

### Verify complete flow

```text
Upload PDF
↓
Extract pages
↓
OCR if necessary
↓
Clean text
↓
Chunk
↓
Embed
↓
Index
↓
Search
↓
Ask question
↓
Retrieve context
↓
Generate grounded answer
↓
Show sources
```

Then verify:

```text
Summary
Flashcards
Quiz
Revision Notes
```

---

# 7. Testing Requirements

Run tests after every major task.

Minimum suite:

```text
tests/
├── test_documents.py
├── test_parsers.py
├── test_chunking.py
├── test_search.py
├── test_rag.py
└── test_study_tools.py
```

Tests must not require paid cloud services.

Use mocks for LLM calls.

---

# 8. Local AI Strategy

Default architecture:

```text
AI Service
   ↓
LLM Adapter
   ↓
Local Runtime
   ↓
Ollama/local model
```

The UI and RAG service must not directly depend on a vendor-specific API.

Keep the adapter small.

Do not implement multiple providers until one local provider works correctly.

---

# 9. Search Strategy

Start with:

```text
keyword score
+
semantic score
=
hybrid score
```

Keep ranking logic simple and deterministic.

Do not introduce learning-to-rank or a complex search engine unless required by measured limitations.

---

# 10. RAG Rules

The RAG system must:

- retrieve before generating
- preserve source metadata
- expose source pages
- avoid unsupported claims
- handle no-results cases
- keep prompt construction separate from retrieval
- keep LLM invocation separate from UI

---

# 11. UI Rules

Streamlit is the presentation layer.

It should call services such as:

```python
document_service.upload(...)
search_service.search(...)
rag_service.ask(...)
study_service.generate_flashcards(...)
```

Do not put parsing, embedding, database schema, or LLM orchestration directly into Streamlit page code.

---

# 12. File Processing Rules

Every upload should have a visible lifecycle:

```text
uploaded
→ processing
→ processed
→ indexed
```

or:

```text
processing
→ failed
```

Failures must preserve useful error information.

---

# 13. Verification Protocol

For every task:

### Step 1 — Inspect

Read only the files relevant to the task.

### Step 2 — Plan

State:

```text
Goal:
Files:
Assumptions:
Implementation:
Verification:
```

### Step 3 — Implement

Make the smallest necessary change.

### Step 4 — Test

Run the focused test.

### Step 5 — Regression check

Run related existing tests.

### Step 6 — Review

Check:

- unnecessary changes
- unused imports
- accidental architecture changes
- missing error paths
- source traceability

### Step 7 — Report

Use:

```text
Completed:
Verification:
Tests:
Files changed:
Known limitations:
Next task:
```

---

# 14. Stop Conditions

Stop and ask the user when:

- requirements conflict
- a decision materially changes architecture
- required behavior cannot be inferred safely
- an external service/API is required but not specified
- a destructive migration is needed
- existing code behavior would be intentionally broken

Do not stop for minor implementation choices that have an obvious simplest solution.

---

# 15. Definition of Done

StudyMate AI is done when:

- application launches
- supported files upload
- metadata persists
- pages persist
- OCR works for scanned content
- chunks are generated
- local embeddings work
- vector index persists
- keyword search works
- semantic search works
- hybrid search works
- RAG works with sources
- summaries work
- flashcards work
- quizzes work
- revision notes work
- core workflow works offline
- tests pass
- README is accurate
- no unnecessary architecture remains

---

# 16. Agent Priority

When choosing between alternatives, prioritize:

```text
1. Correctness
2. Source traceability
3. Simplicity
4. Testability
5. Offline capability
6. Maintainability
7. Performance
8. UI polish
```

Do not sacrifice correctness for speed.

Do not optimize performance before measuring a real bottleneck.

Do not add architecture for hypothetical future requirements.

---

# 17. Final Rule

Build StudyMate AI one verified phase at a time.

Never turn:

```text
"implement feature X"
```

into:

```text
"rewrite the entire project."
```

Every change must have a direct reason, a testable outcome, and a clear relationship to the StudyMate AI requirements.
