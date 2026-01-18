"""Embedding generation and vector storage using LangChain PGVector."""

import io
from contextlib import redirect_stderr, redirect_stdout
from typing import cast
from uuid import UUID

from langchain_postgres import PGVector
from sentence_transformers import SentenceTransformer

from nasi_ayam.ingestion.chunker import VectorChunk
from nasi_ayam.logging import get_logger

logger = get_logger("embedder")

EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_DIMENSIONS = 768
COLLECTION_NAME = "document_chunks"


class Embedder:
    """Handles embedding generation and vector storage."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
        self._model: SentenceTransformer | None = None
        self._vector_store: PGVector | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self._model = SentenceTransformer(
                    EMBEDDING_MODEL, trust_remote_code=True
                )
        return self._model

    @property
    def vector_store(self) -> PGVector:
        if self._vector_store is None:
            logger.info("Initializing PGVector store")
            self._vector_store = PGVector(
                collection_name=COLLECTION_NAME,
                connection=self._database_url,
                embeddings=SentenceTransformerEmbeddings(self.model),  # type: ignore[arg-type]
            )
        return self._vector_store

    def embed_chunks(
        self,
        chunks: list[VectorChunk],
        document_id: UUID,
        source: str,
        doc_type: str,
    ) -> list[str]:
        """Embed vector chunks and store them in the vector database.

        Args:
            chunks: List of vector chunks to embed.
            document_id: The parent document's database ID.
            source: Document source (local/github).
            doc_type: Document type (md/txt/pdf).

        Returns:
            List of IDs assigned to the stored vectors.
        """
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "document_id": str(document_id),
                "source": source,
                "doc_type": doc_type,
                "start_position": chunk.start_position,
                "end_position": chunk.end_position,
                "semantic_chunk_ids": [str(id) for id in chunk.semantic_chunk_ids],
            }
            for chunk in chunks
        ]

        logger.info(f"Embedding {len(chunks)} chunks for document {document_id}")
        ids = self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        logger.debug(f"Stored {len(ids)} vectors")

        return ids

    def delete_by_document(self, document_id: UUID) -> None:
        """Delete all vectors associated with a document."""
        logger.info(f"Deleting vectors for document {document_id}")
        self.vector_store.delete(filter={"document_id": str(document_id)})


class SentenceTransformerEmbeddings:
    """LangChain-compatible wrapper for SentenceTransformer."""

    def __init__(self, model: SentenceTransformer) -> None:
        self._model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return cast(list[list[float]], embeddings.tolist())

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        embedding = self._model.encode(text, convert_to_numpy=True)
        return cast(list[float], embedding.tolist())
