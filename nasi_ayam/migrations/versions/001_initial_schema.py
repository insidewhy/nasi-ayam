"""Initial schema with all custom tables.

Revision ID: 001
Revises:
Create Date: 2025-01-18

"""

from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE documents (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            source VARCHAR(50) NOT NULL,
            file_path TEXT NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            doc_type VARCHAR(10) NOT NULL,
            content_hash VARCHAR(64) NOT NULL,
            file_size BIGINT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE(source, file_path)
        )
    """)

    op.execute("""
        CREATE TABLE semantic_chunks (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            heading_path TEXT NOT NULL,
            start_position INTEGER NOT NULL,
            end_position INTEGER NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE INDEX idx_semantic_chunks_document_id ON semantic_chunks(document_id)
    """)

    op.execute("""
        CREATE TABLE messages (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            is_compacted BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE INDEX idx_messages_created_at ON messages(created_at)
    """)

    op.execute("""
        CREATE TABLE ingestion_log (
            id UUID PRIMARY KEY DEFAULT uuidv7(),
            source_type VARCHAR(50) NOT NULL,
            source_path TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE(source_type, source_path)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ingestion_log")
    op.execute("DROP TABLE IF EXISTS messages")
    op.execute("DROP TABLE IF EXISTS semantic_chunks")
    op.execute("DROP TABLE IF EXISTS documents")
