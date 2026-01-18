"""Chunking logic for documents.

This module provides semantic and vector chunking for documents.
Semantic chunks are logical document sections that provide broader context.
Vector chunks are fixed-size overlapping segments used for embedding and retrieval.
"""

import re
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class DocType(Enum):
    """Document types supported by the chunker."""

    MARKDOWN = "md"
    TEXT = "txt"
    PDF = "pdf"


@dataclass
class SemanticChunk:
    """A semantic chunk extracted from a document."""

    content: str
    heading_path: str
    start_position: int
    end_position: int


@dataclass
class StoredSemanticChunk(SemanticChunk):
    """A semantic chunk with a database ID."""

    id: UUID


@dataclass
class VectorChunk:
    """A vector chunk for embedding and retrieval."""

    content: str
    start_position: int
    end_position: int
    semantic_chunk_ids: list[UUID]


@dataclass
class MarkdownSection:
    """A section of a markdown document under a heading."""

    heading: str
    level: int
    content: str
    start_position: int
    end_position: int
    children: list["MarkdownSection"]


def parse_markdown_structure(content: str) -> list[MarkdownSection]:
    """Parse markdown content into a hierarchical structure of sections.

    Returns a list of top-level sections, each containing nested children.
    Each section's content includes all content under it (including children).
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(content))

    if not matches:
        return []

    sections: list[MarkdownSection] = []

    for i, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start_pos = match.start()

        end_pos = len(content)
        for j in range(i + 1, len(matches)):
            future_level = len(matches[j].group(1))
            if future_level <= level:
                end_pos = matches[j].start()
                break

        section_content = content[start_pos:end_pos]

        sections.append(
            MarkdownSection(
                heading=heading,
                level=level,
                content=section_content,
                start_position=start_pos,
                end_position=end_pos,
                children=[],
            )
        )

    return _build_hierarchy(sections)


def _build_hierarchy(flat_sections: list[MarkdownSection]) -> list[MarkdownSection]:
    """Build a hierarchical tree from a flat list of sections."""
    if not flat_sections:
        return []

    root_sections: list[MarkdownSection] = []
    stack: list[MarkdownSection] = []

    for section in flat_sections:
        while stack and stack[-1].level >= section.level:
            stack.pop()

        if stack:
            stack[-1].children.append(section)
        else:
            root_sections.append(section)

        stack.append(section)

    return root_sections


def _get_heading_path(ancestors: list[str], current_heading: str) -> str:
    """Build a heading path from ancestors and current heading."""
    all_headings = ancestors + [current_heading]
    return " > ".join(all_headings)


def _extract_chunks_from_section(
    section: MarkdownSection,
    max_size: int,
    ancestors: list[str],
) -> list[SemanticChunk]:
    """Extract semantic chunks from a markdown section.

    If the section content fits within max_size, return it as a single chunk.
    Otherwise, recursively process children to find smaller chunks.
    """
    content_size = len(section.content)
    heading_path = _get_heading_path(ancestors, section.heading)

    if content_size <= max_size:
        return [
            SemanticChunk(
                content=section.content,
                heading_path=heading_path,
                start_position=section.start_position,
                end_position=section.end_position,
            )
        ]

    if not section.children:
        return []

    chunks: list[SemanticChunk] = []
    new_ancestors = ancestors + [section.heading]

    for child in section.children:
        chunks.extend(_extract_chunks_from_section(child, max_size, new_ancestors))

    return chunks


def chunk_markdown(content: str, max_chunk_size: int) -> list[SemanticChunk]:
    """Extract semantic chunks from markdown content.

    Prefers larger sections (level 1 headings) when they fit within the limit.
    Falls back to smaller sections (level 2, 3, etc.) when content is too large.

    Args:
        content: The markdown content to chunk.
        max_chunk_size: Maximum size in characters for a semantic chunk.

    Returns:
        A list of semantic chunks extracted from the content.
    """
    sections = parse_markdown_structure(content)

    if not sections:
        if len(content) <= max_chunk_size:
            return [
                SemanticChunk(
                    content=content,
                    heading_path="",
                    start_position=0,
                    end_position=len(content),
                )
            ]
        return []

    chunks: list[SemanticChunk] = []

    for section in sections:
        chunks.extend(_extract_chunks_from_section(section, max_chunk_size, []))

    return chunks


MIN_PARAGRAPH_SIZE = 50


def chunk_text(content: str, max_chunk_size: int) -> list[SemanticChunk]:
    """Extract semantic chunks from plain text content.

    Uses paragraphs (separated by blank lines) as semantic chunks.
    Short leading paragraphs (like titles) are merged with subsequent content.

    Args:
        content: The text content to chunk.
        max_chunk_size: Maximum size in characters for a semantic chunk.

    Returns:
        A list of semantic chunks extracted from the content.
    """
    paragraph_pattern = re.compile(r"\n\s*\n")
    raw_paragraphs = paragraph_pattern.split(content)

    paragraphs: list[str] = []
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue
        if paragraphs and len(paragraphs[-1]) < MIN_PARAGRAPH_SIZE:
            paragraphs[-1] = paragraphs[-1] + "\n\n" + para
        else:
            paragraphs.append(para)

    chunks: list[SemanticChunk] = []
    current_position = 0

    for paragraph in paragraphs:
        first_line = paragraph.split("\n")[0]
        start_pos = content.find(first_line, current_position)
        end_pos = start_pos + len(paragraph)
        current_position = end_pos

        if len(paragraph) <= max_chunk_size:
            chunks.append(
                SemanticChunk(
                    content=paragraph,
                    heading_path=f"Paragraph {len(chunks) + 1}",
                    start_position=start_pos,
                    end_position=end_pos,
                )
            )

    return chunks


def chunk_document(
    content: str,
    doc_type: DocType,
    max_chunk_size: int,
) -> list[SemanticChunk]:
    """Extract semantic chunks from a document based on its type.

    Args:
        content: The document content to chunk.
        doc_type: The type of document (markdown, text, or pdf).
        max_chunk_size: Maximum size in characters for a semantic chunk.

    Returns:
        A list of semantic chunks extracted from the content.
    """
    if doc_type in (DocType.MARKDOWN, DocType.PDF):
        return chunk_markdown(content, max_chunk_size)
    elif doc_type == DocType.TEXT:
        return chunk_text(content, max_chunk_size)
    else:
        return []


def create_vector_chunks(
    content: str,
    chunk_size: int,
    overlap_size: int,
    semantic_chunks: list[StoredSemanticChunk],
) -> list[VectorChunk]:
    """Create fixed-size overlapping vector chunks from content.

    Args:
        content: The document content to chunk.
        chunk_size: Size of each vector chunk in characters.
        overlap_size: Overlap between consecutive chunks in characters.
        semantic_chunks: List of semantic chunks with database IDs for position matching.

    Returns:
        A list of vector chunks with references to parent semantic chunks.
    """
    if not content:
        return []

    chunks: list[VectorChunk] = []
    step = chunk_size - overlap_size
    start = 0

    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunk_content = content[start:end]

        parent_ids = _find_parent_semantic_chunks(start, end, semantic_chunks)

        chunks.append(
            VectorChunk(
                content=chunk_content,
                start_position=start,
                end_position=end,
                semantic_chunk_ids=parent_ids,
            )
        )

        if end >= len(content):
            break

        start += step

    return chunks


def _find_parent_semantic_chunks(
    start: int,
    end: int,
    semantic_chunks: list[StoredSemanticChunk],
) -> list[UUID]:
    """Find semantic chunks that overlap with the given position range.

    A vector chunk belongs to a semantic chunk if any part of it falls within
    the semantic chunk's boundaries.
    """
    parent_ids: list[UUID] = []

    for chunk in semantic_chunks:
        if _ranges_overlap(start, end, chunk.start_position, chunk.end_position):
            parent_ids.append(chunk.id)

    return parent_ids


def _ranges_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
    """Check if two ranges overlap."""
    return start1 < end2 and start2 < end1
