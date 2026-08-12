# StudyMate AI

An offline-first study assistant. Upload PDFs, Word docs, PowerPoint
decks, or scanned images; StudyMate AI extracts and OCRs the text,
indexes it for keyword/semantic/hybrid search, and lets you ask
grounded questions (RAG) or generate summaries, flashcards, quizzes,
and revision notes from your own material.

## Status

Core pipeline implemented and tested: upload → parse → OCR → clean →
chunk → embed → index → search (keyword/semantic/hybrid) → RAG →
study tools (summaries/flashcards/quiz/revision notes) → dashboard.
See "Known limitations" below for what's simplified in this first pass.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### System dependencies

- **Tesseract OCR** must be installed and on your PATH (used for scanned
  documents/images). `pytesseract` is only a wrapper around the `tesseract`
  binary.
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt install tesseract-ocr`
  - Windows: install from the [UB-Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki)

### Local AI (optional but recommended)

StudyMate AI is designed to run fully offline via [Ollama](https://ollama.com):

```bash
ollama serve
ollama pull llama3.1     # or any model you set as LLM_MODEL
```

If no Ollama server is reachable, the app still runs: RAG answers and
study tools fall back to returning the retrieved source text directly
(clearly labeled), instead of a generated answer, so the rest of the
product (upload, search, dashboard) is unaffected.

### Embeddings

By default, embeddings use a small dependency-free local hashing
vectorizer (`EMBEDDING_MODEL=hashing-384`) - no model download required,
so the app works offline out of the box. For higher-quality semantic
search, install `sentence-transformers` and set:

```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

No other code changes are needed - both embedders implement the same
interface (`src/studymate/embeddings/service.py`).

## Running the app

```bash
streamlit run app.py
```

## Running tests

```bash
pytest
# or, without pytest installed:
cd tests && python -m unittest discover -p "test_*.py"
```

Tests use a `FakeLLM` stand-in and never call a cloud service or require
a running Ollama server.

## Project structure

```text
app.py                      Streamlit entry point (navigation only)
src/studymate/
  config/settings.py        Environment-driven settings
  db/                       SQLite schema, models, repositories
  documents/                Upload validation + orchestration
    parsers/                PDF, DOCX, PPTX, image parsers
  ocr/                      Tesseract-based OCR, only runs when needed
  text/                     Cleaning + deterministic chunking
  embeddings/                Local embedding models (hashing / sentence-transformers)
  search/                   Keyword, semantic, hybrid search + vector index
  ai/                       LLM adapter interface + Ollama/extractive implementations
  rag/                      Retrieval-augmented generation pipeline
  study/                    Summaries, flashcards, quizzes, revision notes
  ui/                       Streamlit page renderers
data/
  uploads/                  Original uploaded files
  vectors/                  Persisted vector index
  studymate.db              SQLite database
tests/                      pytest/unittest test suite
```

## Configuration

All settings have defaults; override via environment variables or a
`.env` file (see `.env.example`) - `DATA_DIR`, `EMBEDDING_MODEL`,
`LLM_PROVIDER`, `LLM_MODEL`, `OLLAMA_HOST`, `CHUNK_SIZE`,
`CHUNK_OVERLAP`, `TOP_K`, `OCR_ENABLED`, `MAX_UPLOAD_MB`.

## Supported formats

PDF, DOCX, PPTX, and common image formats (PNG, JPG, TIFF, BMP).

## Known limitations

- The default hashing embedder is bag-of-words, not a trained semantic
  model - it captures exact/overlapping vocabulary well but not deep
  paraphrase similarity. Install `sentence-transformers` for stronger
  semantic search.
- DOCX has no native page boundaries, so a Word document is indexed as
  a single logical page (source attribution is by document, not by
  Word "page").
- The vector index is a single in-memory/on-disk numpy matrix - fine
  for a personal document collection, not built for large multi-user
  corpora.
- Flashcard/quiz source attribution is assigned by round-robin over the
  retrieved chunks used as context, not per-fact provenance from the
  LLM itself (the LLM's JSON output doesn't carry that back).
- RAG/study-tool generation quality depends entirely on the local model
  you run via Ollama; no cloud fallback is implemented by design.
