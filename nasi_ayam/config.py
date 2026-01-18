"""Configuration management via environment variables."""

import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    anthropic_api_key: str
    database_url: str
    chunk_size: int
    overlap_size: int
    semantic_chunk_size: int
    relevant_document_result_count: int
    initial_retrieval_count: int
    max_context_characters: int
    reranker_model: str
    github_data_path: str
    local_data_path: str

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Exits with an error if ANTHROPIC_API_KEY is not set.
        """
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            print(
                "Error: ANTHROPIC_API_KEY environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)

        database_url = os.environ.get(
            "DATABASE_URL",
            "postgresql://nasi_ayam:nasi_ayam@localhost:5432/nasi_ayam",
        )

        return cls(
            anthropic_api_key=anthropic_api_key,
            database_url=database_url,
            chunk_size=int(os.environ.get("CHUNK_SIZE", "2000")),
            overlap_size=int(os.environ.get("OVERLAP_SIZE", "200")),
            semantic_chunk_size=int(os.environ.get("SEMANTIC_CHUNK_SIZE", "8000")),
            relevant_document_result_count=int(
                os.environ.get("RELEVANT_DOCUMENT_RESULT_COUNT", "5")
            ),
            initial_retrieval_count=int(
                os.environ.get("INITIAL_RETRIEVAL_COUNT", "10")
            ),
            max_context_characters=int(
                os.environ.get("MAX_CONTEXT_CHARACTERS", "32000")
            ),
            reranker_model=os.environ.get(
                "RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
            ),
            github_data_path=os.environ.get(
                "GITHUB_DATA_PATH",
                "https://github.com/insidewhy/nasi-ayam/tree/main/example-data/github",
            ),
            local_data_path=os.environ.get("LOCAL_DATA_PATH", "example-data/local"),
        )
