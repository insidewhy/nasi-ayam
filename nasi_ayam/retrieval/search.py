"""Vector search and filtering for document retrieval."""

import io
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from langchain_postgres import PGVector
from sentence_transformers import CrossEncoder, SentenceTransformer

from nasi_ayam.database import (
    get_document_by_id,
    get_cursor,
    get_semantic_chunks_by_ids,
)
from nasi_ayam.ingestion.embedder import (
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    SentenceTransformerEmbeddings,
)
from nasi_ayam.logging import get_logger
from nasi_ayam.progress import ProgressCallback

logger = get_logger("search")


@dataclass
class SearchResult:
    """A search result with vector chunk and parent semantic context."""

    content: str
    score: float
    document_id: UUID
    source: str
    doc_type: str
    file_name: str
    semantic_contexts: list[dict[str, Any]]


class DocumentSearch:
    """Handles semantic search over the vector store with reranking."""

    def __init__(
        self, database_url: str, reranker_model: str, initial_retrieval_count: int
    ) -> None:
        self._database_url = database_url
        self._sqlalchemy_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
        self._reranker_model_name = reranker_model
        self._initial_retrieval_count = initial_retrieval_count
        self._model: SentenceTransformer | None = None
        self._vector_store: PGVector | None = None
        self._reranker: CrossEncoder | None = None
        self._progress_callback: ProgressCallback | None = None

    def set_progress_callback(self, callback: ProgressCallback | None) -> None:
        self._progress_callback = callback

    def _report_progress(self, stage: str, is_starting: bool) -> None:
        if self._progress_callback:
            self._progress_callback(stage, is_starting)

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
            logger.info("Initializing PGVector store for search")
            self._vector_store = PGVector(
                collection_name=COLLECTION_NAME,
                connection=self._sqlalchemy_url,
                embeddings=SentenceTransformerEmbeddings(self.model),  # type: ignore[arg-type]
            )
        return self._vector_store

    @property
    def reranker(self) -> CrossEncoder:
        if self._reranker is None:
            logger.info(f"Loading reranker model: {self._reranker_model_name}")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self._reranker = CrossEncoder(self._reranker_model_name)
        return self._reranker

    def search(
        self,
        query: str,
        top_k: int,
        source: str | None = None,
        doc_type: str | None = None,
    ) -> list[SearchResult]:
        """Search for relevant documents using two-stage retrieval with reranking.

        Args:
            query: The search query.
            top_k: Number of results to return after reranking.
            source: Optional filter by source (local/github).
            doc_type: Optional filter by document type (md/txt/pdf).

        Returns:
            List of search results with reranker scores (higher = better).
        """
        filter_dict: dict[str, str] = {}
        if source:
            filter_dict["source"] = source
        if doc_type:
            filter_dict["doc_type"] = doc_type

        initial_k = self._initial_retrieval_count
        logger.info(
            f"Searching for: {query[:50]}... "
            f"(initial_k={initial_k}, final_k={top_k}, filters={filter_dict})"
        )

        self._report_progress("Searching", True)
        if filter_dict:
            results = self.vector_store.similarity_search_with_score(
                query, k=initial_k, filter=filter_dict
            )
        else:
            results = self.vector_store.similarity_search_with_score(query, k=initial_k)
        self._report_progress("Searched", False)

        if not results:
            return []

        self._report_progress("Reranking", True)
        pairs = [(query, doc.page_content) for doc, _ in results]
        rerank_scores = self.reranker.predict(pairs)

        scored_results = list(zip(results, rerank_scores))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        self._report_progress("Reranked", False)

        all_scores_str = ", ".join(f"{score:.3f}" for _, score in scored_results)
        logger.info(f"Reranked scores: [{all_scores_str}]")

        self._report_progress("Answering", True)

        top_results = scored_results[:top_k]

        search_results: list[SearchResult] = []
        for (doc, _), rerank_score in top_results:
            metadata = doc.metadata
            document_id = UUID(metadata["document_id"])

            semantic_chunk_ids = [
                UUID(id_str) for id_str in metadata.get("semantic_chunk_ids", [])
            ]

            semantic_contexts: list[dict[str, Any]] = []
            file_name = "unknown"

            with get_cursor(self._database_url) as cur:
                if semantic_chunk_ids:
                    semantic_contexts = get_semantic_chunks_by_ids(
                        cur, semantic_chunk_ids
                    )
                document = get_document_by_id(cur, document_id)
                if document:
                    file_name = document["file_name"]

            search_results.append(
                SearchResult(
                    content=doc.page_content,
                    score=float(rerank_score),
                    document_id=document_id,
                    source=metadata["source"],
                    doc_type=metadata["doc_type"],
                    file_name=file_name,
                    semantic_contexts=semantic_contexts,
                )
            )

        return search_results

    def refine_search(
        self,
        new_keywords: str,
        top_k: int,
        source: str | None = None,
        doc_type: str | None = None,
    ) -> list[SearchResult]:
        """Search again with different/expanded keywords.

        This is an alias for search() to support the agent's refine_search tool.
        """
        return self.search(new_keywords, top_k, source, doc_type)
