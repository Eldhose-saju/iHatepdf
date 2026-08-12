# skills.md 

## Purpose

This file defines the implementation skills and operating procedures an AI coding agent should use while developing StudyMate AI.

StudyMate AI is an offline-first document intelligence and study assistant built with Python, Streamlit, SQLite, local embeddings, vector retrieval, and optional local LLM inference.

The agent must follow the four engineering principles from the supplied project guidelines:

- Think Before Coding
- Simplicity First
- Surgical Changes
- Goal-Driven Execution

These principles specifically require assumptions to be surfaced, unnecessary complexity to be avoided, unrelated code to remain untouched, and work to be verified against explicit success criteria.

---

# Skill 1 — Repository Inspection

## Goal

Understand the current repository before implementing anything.

## Steps

1. Inspect the directory tree.
2. Read existing README and configuration.
3. Inspect Python entry points.
4. Inspect dependency files.
5. Inspect tests.
6. Identify existing architecture.
7. Identify code that can be reused.
8. Identify conflicts with StudyMate AI requirements.
9. Do not rewrite working code without a requirement.

## Verification

Produce a short implementation assessment:

```text
Existing structure:
Relevant files:
Reusable components:
Missing components:
Potential conflicts:
Next smallest implementation step:
```

---

# Skill 2 — Project Architecture

## Goal

Keep the application modular without overengineering.

## Rules

Separate:

```text
UI
↓
Application services
↓
Domain processing
↓
Persistence / AI infrastructure
```

Do not let Streamlit pages contain the core document-processing logic.

Do not place database queries throughout UI components.

Do not make every small function into a class.

Use modules when they represent a real responsibility.

---

# Skill 3 — Document Ingestion

## Goal

Convert uploaded study files into normalized page-level text.

## Supported formats

- PDF
- DOCX
- PPTX
- images

## Steps

1. Validate file.
2. Save original.
3. Create document record.
4. Select parser.
5. Extract page/slide-level content.
6. Detect empty/scanned content where relevant.
7. Use OCR when needed.
8. Store page text.
9. Update processing status.
10. Report failure clearly.

## Verification

Each supported format must have at least one automated test.

---

# Skill 4 — OCR

## Goal

Make scanned study material searchable.

## Steps

1. Determine whether OCR is actually required.
2. Convert page/image into OCR-compatible input.
3. Run OCR.
4. Normalize returned text.
5. Store text and OCR status.
6. Preserve page mapping.

## Rules

Do not OCR every page unnecessarily.

Do not silently convert OCR failure into an empty page.

---

# Skill 5 — Text Processing

## Goal

Create clean, retrieval-ready text.

## Steps

1. Normalize whitespace.
2. Remove obvious extraction artifacts.
3. Preserve meaningful structure.
4. Split into deterministic chunks.
5. Preserve document/page metadata.
6. Store chunks.

## Rules

Start with straightforward chunking.

Avoid complex semantic chunking until a measurable requirement exists.

---

# Skill 6 — Embeddings

## Goal

Create local vector representations of study chunks.

## Steps

1. Load configured embedding model.
2. Embed chunks.
3. Persist vectors in a local index.
4. Maintain vector-ID → chunk-ID mapping.
5. Save index to the configured vector directory.

## Verification

- same input produces stable searchable mappings
- vector IDs resolve to real chunks
- index can be loaded after application restart

---

# Skill 7 — Search

Implement three retrieval capabilities:

### Keyword

Useful for:

- exact terminology
- formulas
- names
- identifiers

### Semantic

Useful for:

- paraphrased questions
- conceptual queries
- natural-language search

### Hybrid

Combine both in a simple, testable ranking function.

Every result must retain:

```text
document
page
chunk
score
```

---

# Skill 8 — RAG

## Goal

Answer study questions using retrieved material.

## Pipeline

```text
Question
→ Retrieve
→ Rank
→ Build context
→ Prompt local LLM
→ Generate answer
→ Attach sources
```

## Rules

- Do not answer document-grounded questions from unsupported assumptions.
- Tell the user when retrieval provides insufficient evidence.
- Include source document/page information.
- Keep retrieval and generation independently testable.

---

# Skill 9 — Local AI

## Goal

Keep the core product offline-capable.

Preferred approach:

```text
StudyMate AI
    ↓
LLM adapter
    ↓
Local runtime such as Ollama
```

The rest of the application should not depend directly on one specific LLM vendor.

Do not add cloud APIs unless explicitly requested.

---

# Skill 10 — Study Content Generation

Implement:

- summaries
- flashcards
- quizzes
- revision notes

Every generated object should be associated with its source material where possible.

Example flashcard:

```text
Question
Answer
Source document
Source page
```

Example quiz:

```text
Question
Options
Correct answer
Explanation
Source
```

---

# Skill 11 — Streamlit UI

## Goal

Expose the product through a simple professional interface.

Required sections:

```text
Dashboard
My Materials
Upload
Search
AI Chat
Study Tools
```

Study Tools:

```text
Summarize
Flashcards
Quiz
Revision Notes
```

## UI rules

- Keep processing status visible.
- Show meaningful errors.
- Show source references.
- Avoid duplicating backend logic inside UI.
- Do not spend implementation time on visual polish before functionality works.

---

# Skill 12 — Database

Use SQLite.

Required entities:

```text
documents
pages
chunks
```

Relationships:

```text
Document
  └── Pages
       └── Chunks
```

Keep vector storage separate from relational metadata unless there is a concrete reason to combine them.

---

# Skill 13 — Testing

Use pytest.

## Testing procedure

For a new feature:

```text
Define expected behavior
→ write focused test
→ implement smallest solution
→ run test
→ run relevant existing tests
→ fix regression if introduced
```

Do not make tests dependent on cloud AI services.

Use mocks/fakes for LLM calls where appropriate.

---

# Skill 14 — Error Diagnosis

When something fails:

1. Reproduce it.
2. Read the actual traceback/error.
3. Identify the smallest failing boundary.
4. Fix that boundary.
5. Re-run the failing test.
6. Run relevant regression tests.
7. Do not randomly change multiple layers.

Never respond to an error by adding unrelated dependencies or rewriting the architecture.

---

# Skill 15 — Dependency Management

Add dependencies only when required.

Before adding a package:

- determine whether the standard library already solves the task
- determine whether an existing dependency can solve it
- prefer mature, focused packages

After adding:

- update requirements
- verify import
- verify installation
- add or update relevant tests

---

# Skill 16 — Documentation

Keep:

- README
- agent.md
- skills.md

aligned with the actual implementation.

Do not document features that have not been implemented.

Documentation should explain:

- setup
- dependencies
- project structure
- local AI setup
- running the app
- running tests
- supported formats
- known limitations

---

# Skill 17 — Verification Checklist

Before declaring a phase complete:

```text
[ ] Requirement implemented
[ ] Relevant tests added
[ ] Tests pass
[ ] Application/manual behavior checked
[ ] Errors checked
[ ] No unrelated files changed
[ ] No unnecessary dependencies added
[ ] Documentation updated if needed
```

---

# Skill 18 — Complexity Control

Ask:

> Is this abstraction required today?

If no, do not add it.

Avoid premature:

- repositories for trivial one-query operations
- factories for one implementation
- strategy patterns for one algorithm
- event buses
- service meshes
- background workers
- distributed databases
- cloud infrastructure

StudyMate AI should remain easy for a student developer to understand and maintain.

---

# Skill 19 — Completion Reporting

At the end of every implementation task report:

```text
Implemented:
- ...

Files changed:
- ...

Verification:
- ...

Tests:
- ...

Known limitations:
- ...

Next recommended task:
- ...
```

Never say "fully working" without verification.
