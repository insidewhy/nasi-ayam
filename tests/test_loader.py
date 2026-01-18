"""Tests for the document loaders."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nasi_ayam.ingestion.chunker import DocType
from nasi_ayam.ingestion.loader import (
    calculate_content_hash,
    get_doc_type,
    load_local_documents,
    parse_github_url,
)


class TestCalculateContentHash:
    def test_consistent_hash(self) -> None:
        content = b"test content"
        hash1 = calculate_content_hash(content)
        hash2 = calculate_content_hash(content)
        assert hash1 == hash2

    def test_different_content_different_hash(self) -> None:
        hash1 = calculate_content_hash(b"content a")
        hash2 = calculate_content_hash(b"content b")
        assert hash1 != hash2

    def test_sha256_length(self) -> None:
        hash_value = calculate_content_hash(b"test")
        assert len(hash_value) == 64


class TestGetDocType:
    def test_markdown_extension(self) -> None:
        assert get_doc_type("file.md") == DocType.MARKDOWN
        assert get_doc_type("file.markdown") == DocType.MARKDOWN
        assert get_doc_type("FILE.MD") == DocType.MARKDOWN

    def test_text_extension(self) -> None:
        assert get_doc_type("file.txt") == DocType.TEXT
        assert get_doc_type("FILE.TXT") == DocType.TEXT

    def test_pdf_extension(self) -> None:
        assert get_doc_type("file.pdf") == DocType.PDF
        assert get_doc_type("FILE.PDF") == DocType.PDF

    def test_unsupported_extension(self) -> None:
        assert get_doc_type("file.doc") is None
        assert get_doc_type("file.html") is None
        assert get_doc_type("file") is None


class TestParseGithubUrl:
    def test_valid_url(self) -> None:
        url = "https://github.com/owner/repo/tree/main/path/to/dir"
        owner, repo, branch, path = parse_github_url(url)

        assert owner == "owner"
        assert repo == "repo"
        assert branch == "main"
        assert path == "path/to/dir"

    def test_url_with_different_branch(self) -> None:
        url = "https://github.com/user/project/tree/develop/src/data"
        owner, repo, branch, path = parse_github_url(url)

        assert owner == "user"
        assert repo == "project"
        assert branch == "develop"
        assert path == "src/data"

    def test_invalid_url_format(self) -> None:
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            parse_github_url("https://gitlab.com/owner/repo/tree/main/path")

    def test_missing_path(self) -> None:
        with pytest.raises(ValueError, match="Invalid GitHub URL format"):
            parse_github_url("https://github.com/owner/repo/tree/main")


class TestLoadLocalDocuments:
    def test_loads_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = Path(tmpdir) / "test.md"
            md_file.write_text("# Hello\n\nWorld")

            docs = list(load_local_documents(tmpdir))

            assert len(docs) == 1
            assert docs[0].file_name == "test.md"
            assert docs[0].doc_type == DocType.MARKDOWN
            assert docs[0].content == "# Hello\n\nWorld"
            assert docs[0].source == "local"

    def test_loads_text_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_file = Path(tmpdir) / "test.txt"
            txt_file.write_text("Plain text content")

            docs = list(load_local_documents(tmpdir))

            assert len(docs) == 1
            assert docs[0].file_name == "test.txt"
            assert docs[0].doc_type == DocType.TEXT

    def test_skips_unsupported_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("markdown")
            (Path(tmpdir) / "test.doc").write_text("word doc")
            (Path(tmpdir) / "test.html").write_text("<html>")

            docs = list(load_local_documents(tmpdir))

            assert len(docs) == 1
            assert docs[0].file_name == "test.md"

    def test_directory_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            list(load_local_documents("/nonexistent/path"))

    def test_calculates_content_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "Test content for hashing"
            md_file = Path(tmpdir) / "test.md"
            md_file.write_text(content)

            docs = list(load_local_documents(tmpdir))

            expected_hash = calculate_content_hash(content.encode("utf-8"))
            assert docs[0].content_hash == expected_hash

    def test_calculates_file_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "A" * 100
            md_file = Path(tmpdir) / "test.md"
            md_file.write_text(content)

            docs = list(load_local_documents(tmpdir))

            assert docs[0].file_size == 100

    def test_skips_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "subdir").mkdir()
            (Path(tmpdir) / "test.md").write_text("content")

            docs = list(load_local_documents(tmpdir))

            assert len(docs) == 1

    def test_handles_malformed_file_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            binary_file = Path(tmpdir) / "binary.txt"
            binary_file.write_bytes(b"\xff\xfe invalid utf-8")
            (Path(tmpdir) / "valid.md").write_text("valid content")

            docs = list(load_local_documents(tmpdir))

            assert len(docs) == 1
            assert docs[0].file_name == "valid.md"

    @patch("nasi_ayam.ingestion.loader.convert_pdf_to_markdown")
    def test_converts_pdf_to_markdown(self, mock_convert: MagicMock) -> None:
        mock_convert.return_value = "# PDF Content\n\nExtracted text"

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_file = Path(tmpdir) / "test.pdf"
            pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

            docs = list(load_local_documents(tmpdir))

            assert len(docs) == 1
            assert docs[0].doc_type == DocType.PDF
            assert docs[0].content == "# PDF Content\n\nExtracted text"
            mock_convert.assert_called_once()
