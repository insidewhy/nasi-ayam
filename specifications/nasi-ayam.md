# nasi-ayam, a knowledge retrieval chatbot

## Project brief

### Objective

Design and build a minimal but functional prototype of an "Knowledge Retrieval Chatbot" that demonstrates:

- RAG (Retrieval-Augmented Generation) pipeline
- Agentic reasoning for multi-step queries
- Clear design decision-making

### Context

A company or person has ~10-100 PDF, markdown and text documents scattered across two places:

- Source 1: A local filesystem directory
- Source 2: Files stored in a publicly accessible GitHub directory

The chatbot should answer questions by retrieving and synthesizing information from these sources.

### Overview

- Ingest documents from 2 sources
- Retrieve relevant information intelligently
- Reason through simple multi-step questions, potentially asking follow up questions (agent loop)
- Respond with sourced answers

### Technology

- Use python version `3.13` with LangChain
- Use `mypy` type hints wherever possible
- Use `poetry` to manage python dependencies, `pyenv` is installed so `.python-version` can be used to manage the python version
- Use `docker compose` to run the application, the `postgres` image should contain a health check and the `application` image should have a dependency on the `postgres` image which will cause the `application` to wait for it to be healthy before starting.
  - The `postgres` image should store data via a docker volume so that it will not lose data across restarts.
  - `nvidia-container-toolkit` is available so docker containers should be able to access the GPU, ensure the docker compose enables GPU access
  - The `docker compose` configuration should mount the root directory of the project as a volume rather than statically building the python project, this will allow it to use the most recent source code on each invocation and also to access the documents stored locally in the project. It can assume that the user has already installed dependencies with poetry etc. before running the script.
- All local models should be able to run on a `Intel(R) Core(TM) Ultra 9 185H` and/or a `NVIDIA RTX 2000 Ada Generation Laptop GPU`
  - Note that the system has 32Gb of memory and the Nvidia GPU has 8Gb of memory.
- Use `Alembic` for database migrations (raw SQL migrations, no ORM required)
- Use LangChain's `PGVector` integration for the vector store
- Use `psycopg` for other database operations (conversations, ingestion tracking)
- Use `flake8` to lint python code
- Use `black` to format python code
- Use Python's built-in `logging` module for application logging
  - Log to `logs/app.log` to avoid cluttering the CLI interface
  - Use `RotatingFileHandler` to prevent unbounded log growth (max 10MB, keep 5 backups)
  - Log level configurable via `LOG_LEVEL` environment variable (default: `INFO`)

### Models

- **LLM**: Use `claude-sonnet-4-5-20250929` via the Anthropic API for generation and agentic reasoning
- **Embeddings**: Use `nomic-ai/nomic-embed-text-v1.5` for local embeddings via `sentence-transformers`
  - This model produces 768-dimensional vectors and requires ~550MB VRAM
  - It provides excellent quality while fitting comfortably within the 8GB GPU memory alongside other processes
  - Supports Matryoshka representation (dimensions can be truncated if needed)
- **Reranker**: Use `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking search results
  - This cross-encoder model (~90MB) scores query-document pairs more accurately than vector similarity alone
  - Configurable via `RERANKER_MODEL` environment variable

## Technical requirements

### Knowledge Base Ingestion

- Load documents from 2 sources
  - A publicly accessible github directory
    - Files within the directory can be listed using the github API, don't worry about recursing into child directories
    - The URL of the github directory can be read from an environment variable `GITHUB_DATA_PATH` and should default to `https://github.com/insidewhy/nasi-ayam/tree/main/example-data/github`
  - A directory on the local machine, this can be passed as an environment variable `LOCAL_DATA_PATH` and should default to `example-data/local`

- Chunking strategy
  - PDFs can be converted to markdown using the `pymupdf4llm` library for the purposes of chunking and semantic chunk detection
  - **Vector chunks**: Fixed-size overlapping text segments used for embedding and retrieval
    - Size controlled by `CHUNK_SIZE` environment variable (default: 2000 characters)
    - Overlap controlled by `OVERLAP_SIZE` environment variable (default: 200 characters)
  - **Semantic chunks**: Logical document sections that provide broader context
    - Maximum size controlled by `SEMANTIC_CHUNK_SIZE` environment variable (default: 8000 characters)
    - For markdown/PDF files: sections under headings (prefer level 1, fall back to level 2 if content exceeds limit, etc.)
    - For text files: paragraphs (separated by blank lines)
  - Each vector chunk should store references to its parent semantic chunk(s) when it belongs to one or more viable semantic chunks
    - Due to overlapping, a vector chunk may span 0-n semantic chunks (e.g., crossing a heading boundary)
    - There may not always be a parent semantic chunk available e.g. if the chunk belongs to a semantic chunk that exceeds the semantic chunk size limit
    - Store an array of `semantic_chunk_ids` in the LangChain PGVector metadata field
    - On retrieval, use these IDs to fetch parent semantic chunk content from the `semantic_chunks` table

- Store chunks in a PostgreSQL 18 database using the pgvector extension.
  - Use UUIDv7 for all primary keys (time-ordered for better index performance)
  - Vector chunks are managed by LangChain's PGVector integration (automatic table creation)
  - Semantic chunks and document metadata are stored in custom tables managed via Alembic

### Retrieval system

- Two-stage retrieval with reranking:
  1. Vector search retrieves initial candidates (`INITIAL_RETRIEVAL_COUNT`, default: 10)
  2. Cross-encoder reranker scores query-document pairs and returns top results (`RELEVANT_DOCUMENT_RESULT_COUNT`, default: 5)
- Metadata filtering (e.g. document source or document type)

### Generation with context

- Use the Claude LLM API to generate answers, the Anthropic key can be read from the `ANTHROPIC_API_KEY` environment variable and the process should fail to start if this is not supplied
- Include citations to source documents
- Handle multi-turn conversation
  - Conversation history should be stored in a postgres table, allowing the conversation to resume across invocations
  - There is a single persistent conversation - all messages belong to one continuous session
  - **Compaction**: When conversation history exceeds `MAX_CONTEXT_CHARACTERS` (default: 32000 characters):
    1. Summarize older messages into a condensed context summary using the LLM
    2. Replace the older messages with the summary in the database
    3. Keep recent messages (last 4-6 exchanges) intact for immediate context

### Agentic capability (minimal)

- Implement a simple agent loop using LangChain's tool-calling capabilities
- The agent should have access to these tools:
  1. `search_documents(query: str, source: Optional[str], doc_type: Optional[str])` - search with optional filters
  2. `refine_search(new_keywords: str)` - search again with different/expanded keywords
- Decision logic: The LLM decides whether retrieved context is sufficient to answer, or if it needs to search again with different terms
- Limit agent iterations to prevent infinite loops (max 3 retrieval attempts per query)

### Interface

- This will operate as a command-line application
- On startup it will:
  - Ensure database migration state is up to date
  - Pause if all documents have not been ingested, then inform the user when ingestion is complete and begin accepting prompts
- The ingestion process should be able to validate when a source (e.g. github directory, local directory) has already been ingested, and skip ingestion if it has occurred within the last 24 hours.
- When a source is reingested it should skip processing documents that have already been processed.
- Document change detection should use file content hashes (SHA-256) to identify modified files
- When a previously ingested file has changed, delete its old chunks and re-ingest
- After ingestion is complete it will prompt the user for input, then generate output. During output generation it will show a loading indicator and not accept further input. When output has been generated, the user may then ask follow up questions and context will be maintained.
- It should show locations of retrieved sources

## Invocation

A bash script should be provided at `./nasi-ayam` which will run the application via `docker compose` as described above.

If the application is invoked with a parameter it should send this query after ingestion is complete, then the application should exit when it has finished adding the prompt to the user's prompt history, compacting (if necessary) and displaying the answer.

## Implementation notes

- A `Makefile` should be available in the project root the following targets:
  - `reset-postgres`: Shut down the postgres container and remove its associated volume e.g. via `docker compose down -v`
  - `psql`: Run `psql` session against the database for debugging purposes.
  - `typecheck`: Run `mypy` against the source code
  - `format`: Run `black` against the source code
  - `lint`: Run `flake8` against the source code
  - `validate`: Should have `format`, `lint` and `typecheck` as dependencies
- A github action workflow should exist to validate formatting, type checks and linting

## Database Schema

The `PostgreSQL 18` database with `pgvector` extension should contain these tables (managed via Alembic migrations). All primary keys should use `UUIDv7`:

**Managed by LangChain PGVector:**
- **langchain_pg_collection**: Vector collection metadata (created automatically)
- **langchain_pg_embedding**: Vector chunks with embeddings (created automatically)

**Custom tables (via Alembic):**

- **documents**: Metadata about ingested files
  - id (UUID), source (github/local), file_path, file_name, doc_type (pdf/md/txt), content_hash (SHA-256), file_size, created_at, updated_at

- **semantic_chunks**: Logical document sections for context
  - id (UUID), document_id (FK), content, heading_path (e.g. "Main > Sub"), start_position, end_position, created_at, updated_at

- **messages**: Conversation history (single persistent conversation across all invocations)
  - id (UUID), role (user/assistant), content, is_compacted (boolean), created_at

- **ingestion_log**: Track source ingestion times
  - id (UUID), source_type, source_path, created_at, updated_at

## Error Handling

- **Network failures**: Retry GitHub API requests up to 3 times with exponential backoff. Log failures and continue with available documents.
- **Malformed documents**: Log a warning and skip the document rather than failing the entire ingestion
- **API rate limiting**: Implement exponential backoff for Claude API calls
- **Missing API key**: Exit immediately with a clear error message

## Project Structure

```
nasi-ayam/                           # project root
├── nasi_ayam/                       # Python package
│   ├── __init__.py
│   ├── main.py                      # CLI entry point
│   ├── config.py                    # Environment variable handling
│   ├── database.py                  # Database connection and queries
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py                # Document loaders (local, github)
│   │   ├── chunker.py               # Chunking logic
│   │   └── embedder.py              # Embedding generation
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── search.py                # Vector search and filtering
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── agent.py                 # Agentic reasoning loop
│   │   └── conversation.py          # Conversation management
│   └── migrations/                  # Alembic migrations
│       ├── env.py
│       └── versions/
├── example-data/
│   ├── local/
│   ├── github/
│   └── suggested-prompts.md
├── logs/                            # Application logs (gitignored)
│   └── app.log
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── Makefile
└── nasi-ayam                        # Entry script (runs via docker compose)
```

## Configuration Defaults


| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | 2000 | Vector chunk size in characters |
| `OVERLAP_SIZE` | 200 | Overlap between chunks in characters |
| `SEMANTIC_CHUNK_SIZE` | 8000 | Maximum semantic chunk size in characters |
| `RELEVANT_DOCUMENT_RESULT_COUNT` | 5 | Number of documents to return after reranking |
| `INITIAL_RETRIEVAL_COUNT` | 10 | Number of documents to retrieve before reranking |
| `MAX_CONTEXT_CHARACTERS` | 32000 | Trigger compaction above this |
| `RERANKER_MODEL` | cross-encoder/ms-marco-MiniLM-L-6-v2 | Cross-encoder model for reranking |
| `LOCAL_DATA_PATH` | example-data/local | Local documents directory |
| `GITHUB_DATA_PATH` | (see below) | GitHub documents directory |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |


Default `GITHUB_DATA_PATH`: `https://github.com/insidewhy/nasi-ayam/tree/main/example-data/github`
