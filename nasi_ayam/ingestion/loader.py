"""Document loaders for local filesystem and GitHub."""

import contextlib
import hashlib
import io
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, cast

import httpx

with contextlib.redirect_stdout(io.StringIO()):
    import pymupdf4llm  # type: ignore[import-untyped]

from nasi_ayam.ingestion.chunker import DocType
from nasi_ayam.logging import get_logger

logger = get_logger("loader")


@dataclass
class LoadedDocument:
    """A document loaded from a source."""

    source: str
    file_path: str
    file_name: str
    doc_type: DocType
    content: str
    content_hash: str
    file_size: int


def calculate_content_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of content."""
    return hashlib.sha256(content).hexdigest()


def get_doc_type(filename: str) -> DocType | None:
    """Determine document type from filename extension."""
    lower = filename.lower()
    if lower.endswith(".md") or lower.endswith(".markdown"):
        return DocType.MARKDOWN
    elif lower.endswith(".txt"):
        return DocType.TEXT
    elif lower.endswith(".pdf"):
        return DocType.PDF
    return None


def convert_pdf_to_markdown(pdf_path: str | Path) -> str:
    """Convert a PDF file to markdown using pymupdf4llm."""
    return cast(str, pymupdf4llm.to_markdown(str(pdf_path)))


def load_local_documents(directory: str) -> Iterator[LoadedDocument]:
    """Load documents from a local directory.

    Args:
        directory: Path to the local directory.

    Yields:
        LoadedDocument for each supported file found.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    logger.info(f"Loading documents from local directory: {directory}")

    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue

        doc_type = get_doc_type(file_path.name)
        if doc_type is None:
            logger.debug(f"Skipping unsupported file: {file_path.name}")
            continue

        try:
            raw_content = file_path.read_bytes()
            content_hash = calculate_content_hash(raw_content)
            file_size = len(raw_content)

            if doc_type == DocType.PDF:
                logger.debug(f"Converting PDF to markdown: {file_path.name}")
                content = convert_pdf_to_markdown(file_path)
            else:
                content = raw_content.decode("utf-8")

            logger.info(f"Loaded document: {file_path.name} ({file_size} bytes)")

            yield LoadedDocument(
                source="local",
                file_path=str(file_path),
                file_name=file_path.name,
                doc_type=doc_type,
                content=content,
                content_hash=content_hash,
                file_size=file_size,
            )
        except Exception as e:
            logger.warning(f"Failed to load {file_path.name}: {e}")
            continue


def parse_github_url(url: str) -> tuple[str, str, str, str]:
    """Parse a GitHub directory URL into components.

    Args:
        url: GitHub URL like https://github.com/owner/repo/tree/branch/path

    Returns:
        Tuple of (owner, repo, branch, path)
    """
    pattern = r"https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    return match.groups()  # type: ignore


def github_api_request(
    url: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> httpx.Response:
    """Make a GitHub API request with retry logic.

    Args:
        url: The API URL to request.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay between retries (doubles each retry).

    Returns:
        The HTTP response.

    Raises:
        httpx.HTTPStatusError: If all retries fail.
    """
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers={"Accept": "application/vnd.github.v3+json"},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries:
                logger.error(
                    f"GitHub API request failed after {max_retries} retries: {e}"
                )
                raise
            logger.warning(f"GitHub API request failed (attempt {attempt + 1}): {e}")
            time.sleep(delay)
            delay *= 2

    raise RuntimeError("Unreachable")


def load_github_documents(github_url: str) -> Iterator[LoadedDocument]:
    """Load documents from a GitHub directory.

    Args:
        github_url: GitHub directory URL.

    Yields:
        LoadedDocument for each supported file found.
    """
    owner, repo, branch, path = parse_github_url(github_url)
    api_url = (
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    )

    logger.info(f"Loading documents from GitHub: {github_url}")

    response = github_api_request(api_url)
    contents = response.json()

    for item in contents:
        if item.get("type") != "file":
            continue

        filename = item["name"]
        doc_type = get_doc_type(filename)
        if doc_type is None:
            logger.debug(f"Skipping unsupported file: {filename}")
            continue

        try:
            download_url = item["download_url"]
            file_response = github_api_request(download_url)
            raw_content = file_response.content
            content_hash = calculate_content_hash(raw_content)
            file_size = len(raw_content)

            if doc_type == DocType.PDF:
                logger.debug(f"Converting PDF to markdown: {filename}")
                content = convert_pdf_from_bytes(raw_content)
            else:
                content = raw_content.decode("utf-8")

            logger.info(f"Loaded document from GitHub: {filename} ({file_size} bytes)")

            yield LoadedDocument(
                source="github",
                file_path=item["path"],
                file_name=filename,
                doc_type=doc_type,
                content=content,
                content_hash=content_hash,
                file_size=file_size,
            )
        except Exception as e:
            logger.warning(f"Failed to load {filename} from GitHub: {e}")
            continue


def convert_pdf_from_bytes(pdf_bytes: bytes) -> str:
    """Convert PDF bytes to markdown.

    Uses a temporary file since pymupdf4llm requires a file path.
    """
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        return cast(str, pymupdf4llm.to_markdown(tmp.name))
