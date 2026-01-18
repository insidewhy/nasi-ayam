"""Database connection and query management."""

from contextlib import contextmanager
from typing import Any, Generator, cast
from uuid import UUID

import psycopg
from psycopg.rows import dict_row


def get_connection(database_url: str) -> psycopg.Connection[dict[str, Any]]:
    """Create a new database connection."""
    return psycopg.connect(database_url, row_factory=dict_row)


@contextmanager
def get_cursor(
    database_url: str,
) -> Generator[psycopg.Cursor[dict[str, Any]], None, None]:
    """Context manager for database cursor with automatic commit/rollback."""
    conn = get_connection(database_url)
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_document(
    cur: psycopg.Cursor[dict[str, Any]],
    source: str,
    file_path: str,
    file_name: str,
    doc_type: str,
    content_hash: str,
    file_size: int,
) -> UUID:
    """Insert a new document record and return its ID."""
    cur.execute(
        """
        INSERT INTO documents (source, file_path, file_name, doc_type, content_hash, file_size)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (source, file_path, file_name, doc_type, content_hash, file_size),
    )
    result = cur.fetchone()
    assert result is not None
    return cast(UUID, result["id"])


def get_document_by_path(
    cur: psycopg.Cursor[dict[str, Any]],
    source: str,
    file_path: str,
) -> dict[str, Any] | None:
    """Get a document by its source and path."""
    cur.execute(
        """
        SELECT * FROM documents WHERE source = %s AND file_path = %s
        """,
        (source, file_path),
    )
    return cur.fetchone()


def get_document_by_id(
    cur: psycopg.Cursor[dict[str, Any]],
    document_id: UUID,
) -> dict[str, Any] | None:
    """Get a document by its ID."""
    cur.execute(
        """
        SELECT * FROM documents WHERE id = %s
        """,
        (document_id,),
    )
    return cur.fetchone()


def delete_document(cur: psycopg.Cursor[dict[str, Any]], document_id: UUID) -> None:
    """Delete a document and its associated semantic chunks."""
    cur.execute("DELETE FROM semantic_chunks WHERE document_id = %s", (document_id,))
    cur.execute("DELETE FROM documents WHERE id = %s", (document_id,))


def insert_semantic_chunk(
    cur: psycopg.Cursor[dict[str, Any]],
    document_id: UUID,
    content: str,
    heading_path: str,
    start_position: int,
    end_position: int,
) -> UUID:
    """Insert a new semantic chunk and return its ID."""
    cur.execute(
        """
        INSERT INTO semantic_chunks (document_id, content, heading_path, start_position, end_position)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (document_id, content, heading_path, start_position, end_position),
    )
    result = cur.fetchone()
    assert result is not None
    return cast(UUID, result["id"])


def get_semantic_chunks_by_ids(
    cur: psycopg.Cursor[dict[str, Any]],
    chunk_ids: list[UUID],
) -> list[dict[str, Any]]:
    """Get semantic chunks by their IDs."""
    if not chunk_ids:
        return []
    cur.execute(
        """
        SELECT * FROM semantic_chunks WHERE id = ANY(%s)
        """,
        (chunk_ids,),
    )
    return list(cur.fetchall())


def insert_message(
    cur: psycopg.Cursor[dict[str, Any]],
    role: str,
    content: str,
    is_compacted: bool = False,
) -> UUID:
    """Insert a new message and return its ID."""
    cur.execute(
        """
        INSERT INTO messages (role, content, is_compacted)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (role, content, is_compacted),
    )
    result = cur.fetchone()
    assert result is not None
    return cast(UUID, result["id"])


def get_messages(
    cur: psycopg.Cursor[dict[str, Any]],
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Get all messages ordered by creation time."""
    query = "SELECT * FROM messages ORDER BY created_at ASC"
    if limit:
        query += f" LIMIT {limit}"
    cur.execute(query)
    return list(cur.fetchall())


def get_message_count(cur: psycopg.Cursor[dict[str, Any]]) -> int:
    """Get the total character count of all messages."""
    cur.execute("SELECT COALESCE(SUM(LENGTH(content)), 0) as total FROM messages")
    result = cur.fetchone()
    assert result is not None
    return int(result["total"])


def delete_messages_before(
    cur: psycopg.Cursor[dict[str, Any]],
    before_id: UUID,
) -> int:
    """Delete messages created before the given ID. Returns count deleted."""
    cur.execute(
        """
        DELETE FROM messages
        WHERE created_at < (SELECT created_at FROM messages WHERE id = %s)
        """,
        (before_id,),
    )
    return cur.rowcount


def mark_messages_compacted(
    cur: psycopg.Cursor[dict[str, Any]],
    message_ids: list[UUID],
) -> None:
    """Mark messages as compacted."""
    if not message_ids:
        return
    cur.execute(
        """
        UPDATE messages SET is_compacted = TRUE WHERE id = ANY(%s)
        """,
        (message_ids,),
    )


def clear_messages(cur: psycopg.Cursor[dict[str, Any]]) -> int:
    """Delete all messages. Returns count deleted."""
    cur.execute("DELETE FROM messages")
    return cur.rowcount


def get_ingestion_log(
    cur: psycopg.Cursor[dict[str, Any]],
    source_type: str,
    source_path: str,
) -> dict[str, Any] | None:
    """Get the most recent ingestion log for a source."""
    cur.execute(
        """
        SELECT * FROM ingestion_log
        WHERE source_type = %s AND source_path = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (source_type, source_path),
    )
    return cur.fetchone()


def upsert_ingestion_log(
    cur: psycopg.Cursor[dict[str, Any]],
    source_type: str,
    source_path: str,
) -> UUID:
    """Insert or update an ingestion log entry."""
    cur.execute(
        """
        INSERT INTO ingestion_log (source_type, source_path)
        VALUES (%s, %s)
        ON CONFLICT (source_type, source_path)
        DO UPDATE SET updated_at = now()
        RETURNING id
        """,
        (source_type, source_path),
    )
    result = cur.fetchone()
    assert result is not None
    return cast(UUID, result["id"])
