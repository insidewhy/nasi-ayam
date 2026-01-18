"""Main CLI entry point for nasi-ayam."""

import io
import sys
from contextlib import redirect_stderr, redirect_stdout

from nasi_ayam.spinner import Spinner

# Start loading spinner immediately before heavy imports
_loading_spinner = Spinner("Loading")
_loading_spinner.start()

# Set up logging before heavy imports
from nasi_ayam.logging import get_logger, setup_logging  # noqa: E402

setup_logging()

logger = get_logger("main")

# Now do heavy imports (noqa: E402 for all - intentionally after spinner code)
from datetime import datetime, timezone  # noqa: E402

from alembic import command  # noqa: E402
from alembic.config import Config as AlembicConfig  # noqa: E402

from nasi_ayam.config import Config  # noqa: E402
from nasi_ayam.database import (  # noqa: E402
    clear_messages,
    delete_document,
    get_cursor,
    get_document_by_path,
    get_ingestion_log,
    insert_document,
    insert_semantic_chunk,
    upsert_ingestion_log,
)
from nasi_ayam.generation.agent import RetrievalAgent  # noqa: E402
from nasi_ayam.progress import ProgressCallback  # noqa: E402
from nasi_ayam.ingestion.chunker import (  # noqa: E402
    StoredSemanticChunk,
    chunk_document,
    create_vector_chunks,
)
from nasi_ayam.ingestion.embedder import Embedder  # noqa: E402
from nasi_ayam.ingestion.loader import (  # noqa: E402
    LoadedDocument,
    load_github_documents,
    load_local_documents,
)

# Stop the loading spinner (no newline so ingestion status appears on same line)
_loading_spinner.stop("Loaded", newline=False)

INGESTION_SKIP_HOURS = 24


def _run_migrations(database_url: str) -> None:
    """Run any pending database migrations."""
    logger.info("Running database migrations")
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        command.upgrade(alembic_cfg, "head")
    logger.info("Migrations complete")


def _should_skip_ingestion(
    database_url: str, source_type: str, source_path: str
) -> bool:
    """Check if we should skip ingestion for a source."""
    with get_cursor(database_url) as cur:
        log = get_ingestion_log(cur, source_type, source_path)
        if log is None:
            return False

        last_updated = log["updated_at"]
        if last_updated.tzinfo is None:
            last_updated = last_updated.replace(tzinfo=timezone.utc)

        hours_since = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600
        return bool(hours_since < INGESTION_SKIP_HOURS)


def ingest_document(
    database_url: str,
    embedder: Embedder,
    doc: LoadedDocument,
    semantic_chunk_size: int,
    chunk_size: int,
    overlap_size: int,
) -> bool:
    """Ingest a single document. Returns True if ingested, False if skipped."""
    with get_cursor(database_url) as cur:
        existing = get_document_by_path(cur, doc.source, doc.file_path)

        if existing:
            if existing["content_hash"] == doc.content_hash:
                logger.debug(f"Skipping unchanged document: {doc.file_name}")
                return False

            logger.info(f"Re-ingesting changed document: {doc.file_name}")
            embedder.delete_by_document(existing["id"])
            delete_document(cur, existing["id"])

        document_id = insert_document(
            cur,
            doc.source,
            doc.file_path,
            doc.file_name,
            doc.doc_type.value,
            doc.content_hash,
            doc.file_size,
        )

        semantic_chunks = chunk_document(doc.content, doc.doc_type, semantic_chunk_size)

        stored_chunks: list[StoredSemanticChunk] = []
        for chunk in semantic_chunks:
            chunk_id = insert_semantic_chunk(
                cur,
                document_id,
                chunk.content,
                chunk.heading_path,
                chunk.start_position,
                chunk.end_position,
            )
            stored_chunks.append(
                StoredSemanticChunk(
                    content=chunk.content,
                    heading_path=chunk.heading_path,
                    start_position=chunk.start_position,
                    end_position=chunk.end_position,
                    id=chunk_id,
                )
            )

    vector_chunks = create_vector_chunks(
        doc.content, chunk_size, overlap_size, stored_chunks
    )

    embedder.embed_chunks(
        vector_chunks,
        document_id,
        doc.source,
        doc.doc_type.value,
    )

    logger.info(
        f"Ingested: {doc.file_name} ({len(stored_chunks)} semantic, {len(vector_chunks)} vector chunks)"
    )
    return True


def ingest_local_documents(config: Config, embedder: Embedder) -> int:
    """Ingest documents from the local directory. Returns count ingested."""
    source_type = "local"
    source_path = config.local_data_path

    count = 0
    try:
        for doc in load_local_documents(source_path):
            if ingest_document(
                config.database_url,
                embedder,
                doc,
                config.semantic_chunk_size,
                config.chunk_size,
                config.overlap_size,
            ):
                count += 1
    except FileNotFoundError:
        logger.warning(f"Local data directory not found: {source_path}")
        return 0

    with get_cursor(config.database_url) as cur:
        upsert_ingestion_log(cur, source_type, source_path)

    return count


def ingest_github_documents(config: Config, embedder: Embedder) -> int:
    """Ingest documents from the GitHub directory. Returns count ingested."""
    source_type = "github"
    source_path = config.github_data_path

    count = 0
    try:
        for doc in load_github_documents(source_path):
            if ingest_document(
                config.database_url,
                embedder,
                doc,
                config.semantic_chunk_size,
                config.chunk_size,
                config.overlap_size,
            ):
                count += 1
    except Exception as e:
        logger.warning(f"Failed to ingest from GitHub: {e}")
        return 0

    with get_cursor(config.database_url) as cur:
        upsert_ingestion_log(cur, source_type, source_path)

    return count


def _run_ingestion(config: Config) -> None:
    """Run document ingestion from all sources."""
    spinner = Spinner("Ingesting", inline=True)
    spinner.start()

    local_skip = _should_skip_ingestion(
        config.database_url, "local", config.local_data_path
    )
    github_skip = _should_skip_ingestion(
        config.database_url, "github", config.github_data_path
    )

    if local_skip and github_skip:
        spinner.stop("Ingestion up to date")
        return

    total = 0
    try:
        embedder = Embedder(config.database_url)
        if not local_skip:
            total += ingest_local_documents(config, embedder)
        if not github_skip:
            total += ingest_github_documents(config, embedder)
    finally:
        if total > 0:
            spinner.stop(f"Ingested {total} document(s)")
        else:
            spinner.stop("Ingestion complete: all documents up to date")


def _interactive_loop(agent: RetrievalAgent) -> None:
    """Run the interactive query loop."""
    print("\nReady for questions. Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue

        if query.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        state, progress_callback = _create_progress_callback()
        agent.set_progress_callback(progress_callback)

        try:
            response = agent.process_query(query)
            print(f"Assistant: {response}\n")

            sources = agent.get_last_results()
            if sources:
                print("Sources:")
                seen = set()
                for result in sources:
                    if result.file_name not in seen:
                        seen.add(result.file_name)
                        print(f"  - {result.file_name}")
                print()
        except Exception as e:
            spinner = state["spinner"]
            if isinstance(spinner, Spinner):
                spinner.stop("Error")
            print(f"Error: {e}\n")
            logger.error(f"Query error: {e}", exc_info=True)


def _create_progress_callback() -> (
    tuple[dict[str, Spinner | None | bool], ProgressCallback]
):
    """Create a progress callback that manages a spinner."""
    state: dict[str, Spinner | None | bool] = {"spinner": None, "first": True}

    def callback(stage: str, is_starting: bool) -> None:
        if is_starting:
            is_first = state["first"]
            state["first"] = False
            new_spinner = Spinner(stage, inline=not is_first)
            new_spinner.start()
            state["spinner"] = new_spinner
        else:
            current_spinner = state["spinner"]
            if isinstance(current_spinner, Spinner):
                is_final = stage == "Answered"
                current_spinner.stop(stage, newline=is_final)
                state["spinner"] = None

    return state, callback


def single_query(agent: RetrievalAgent, query: str) -> None:
    """Process a single query and exit."""
    state, progress_callback = _create_progress_callback()
    agent.set_progress_callback(progress_callback)

    try:
        response = agent.process_query(query)
        print(response)

        sources = agent.get_last_results()
        if sources:
            print("\nSources:")
            seen = set()
            for result in sources:
                if result.file_name not in seen:
                    seen.add(result.file_name)
                    print(f"  - {result.file_name}")
    except Exception as e:
        spinner = state["spinner"]
        if isinstance(spinner, Spinner):
            spinner.stop("Error")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    setup_logging()
    logger.info("Starting nasi-ayam")

    clear_history = "-c" in sys.argv
    if clear_history:
        sys.argv.remove("-c")

    ingest_only = "-i" in sys.argv
    if ingest_only:
        sys.argv.remove("-i")

    config = Config.from_env()

    if clear_history:
        _run_migrations(config.database_url)
        with get_cursor(config.database_url) as cur:
            count = clear_messages(cur)
        print(f"Cleared {count} message(s)")
        return

    _run_migrations(config.database_url)

    _run_ingestion(config)

    if ingest_only:
        return

    agent = RetrievalAgent(
        database_url=config.database_url,
        anthropic_api_key=config.anthropic_api_key,
        relevant_document_result_count=config.relevant_document_result_count,
        initial_retrieval_count=config.initial_retrieval_count,
        max_context_characters=config.max_context_characters,
        reranker_model=config.reranker_model,
    )

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        single_query(agent, query)
    else:
        _interactive_loop(agent)


if __name__ == "__main__":
    main()
