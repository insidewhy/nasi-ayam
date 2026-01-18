"""Tests for the semantic and vector chunker."""

from uuid import UUID

from nasi_ayam.ingestion.chunker import (
    DocType,
    StoredSemanticChunk,
    chunk_document,
    chunk_markdown,
    chunk_text,
    create_vector_chunks,
    parse_markdown_structure,
)


class TestParseMarkdownStructure:
    """Tests for parsing markdown into a hierarchical structure."""

    def test_empty_content(self) -> None:
        sections = parse_markdown_structure("")
        assert sections == []

    def test_no_headings(self) -> None:
        content = "Just some text without any headings."
        sections = parse_markdown_structure(content)
        assert sections == []

    def test_single_level1_heading(self) -> None:
        content = "# Heading 1\n\nSome content here."
        sections = parse_markdown_structure(content)
        assert len(sections) == 1
        assert sections[0].heading == "Heading 1"
        assert sections[0].level == 1

    def test_multiple_level1_headings(self) -> None:
        content = "# First\n\nContent 1\n\n# Second\n\nContent 2"
        sections = parse_markdown_structure(content)
        assert len(sections) == 2
        assert sections[0].heading == "First"
        assert sections[1].heading == "Second"

    def test_nested_headings(self) -> None:
        content = "# Level 1\n\n## Level 2\n\nContent"
        sections = parse_markdown_structure(content)
        assert len(sections) == 1
        assert sections[0].heading == "Level 1"
        assert len(sections[0].children) == 1
        assert sections[0].children[0].heading == "Level 2"

    def test_deeply_nested_headings(self) -> None:
        content = "# H1\n\n## H2\n\n### H3\n\n#### H4\n\nDeep content"
        sections = parse_markdown_structure(content)
        assert len(sections) == 1
        assert sections[0].level == 1
        h2 = sections[0].children[0]
        assert h2.level == 2
        h3 = h2.children[0]
        assert h3.level == 3
        h4 = h3.children[0]
        assert h4.level == 4


class TestChunkMarkdown:
    """Tests for markdown semantic chunking."""

    def test_small_level1_section_returns_single_chunk(self) -> None:
        """When level 1 content fits within limit, return it as one chunk."""
        content = "# Cats\n\nCats are wonderful pets. They are fluffy and cute."
        chunks = chunk_markdown(content, max_chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].heading_path == "Cats"
        assert "Cats are wonderful pets" in chunks[0].content

    def test_large_level1_falls_back_to_level2(self) -> None:
        """When level 1 content exceeds limit, fall back to level 2 sections."""
        content = """# Main Topic

## Subtopic A

This is content for subtopic A. It has some detailed information.

## Subtopic B

This is content for subtopic B. It also has detailed information.
"""
        chunks = chunk_markdown(content, max_chunk_size=100)

        assert len(chunks) == 2
        assert chunks[0].heading_path == "Main Topic > Subtopic A"
        assert chunks[1].heading_path == "Main Topic > Subtopic B"

    def test_level2_falls_back_to_level3(self) -> None:
        """When level 2 content exceeds limit, fall back to level 3 sections."""
        content = """# Main

## Section

### Part 1

Content for part 1.

### Part 2

Content for part 2.
"""
        chunks = chunk_markdown(content, max_chunk_size=50)

        assert len(chunks) == 2
        assert chunks[0].heading_path == "Main > Section > Part 1"
        assert chunks[1].heading_path == "Main > Section > Part 2"

    def test_mixed_sizes_uses_largest_possible(self) -> None:
        """Some sections fit at level 1, others need level 2."""
        content = """# Small Section

Short content.

# Large Section

## Sub A

Content A is here with more text and extra details to make it longer.

## Sub B

Content B is here with more text and extra details to make it longer.
"""
        chunks = chunk_markdown(content, max_chunk_size=100)

        heading_paths = [c.heading_path for c in chunks]
        assert "Small Section" in heading_paths
        assert "Large Section > Sub A" in heading_paths
        assert "Large Section > Sub B" in heading_paths

    def test_content_without_headings_small(self) -> None:
        """Content without headings that fits within limit."""
        content = "Just some plain text without any markdown headings."
        chunks = chunk_markdown(content, max_chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].heading_path == ""
        assert chunks[0].content == content

    def test_content_without_headings_large(self) -> None:
        """Content without headings that exceeds limit returns empty."""
        content = "A" * 1000
        chunks = chunk_markdown(content, max_chunk_size=100)

        assert len(chunks) == 0

    def test_preserves_positions(self) -> None:
        """Chunk positions correctly reference the original content."""
        content = "# Heading\n\nSome content here."
        chunks = chunk_markdown(content, max_chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].start_position == 0
        assert chunks[0].end_position == len(content)
        assert content[chunks[0].start_position : chunks[0].end_position] == content

    def test_multiple_top_level_sections(self) -> None:
        """Multiple independent level 1 sections."""
        content = """# Cats

Cats are great.

# Dogs

Dogs are also great.

# Birds

Birds can fly.
"""
        chunks = chunk_markdown(content, max_chunk_size=500)

        assert len(chunks) == 3
        assert chunks[0].heading_path == "Cats"
        assert chunks[1].heading_path == "Dogs"
        assert chunks[2].heading_path == "Birds"

    def test_section_too_large_with_no_children_excluded(self) -> None:
        """A section that's too large with no children is excluded."""
        content = """# Small

OK.

# Huge

""" + "X" * 500

        chunks = chunk_markdown(content, max_chunk_size=100)

        assert len(chunks) == 1
        assert chunks[0].heading_path == "Small"


class TestChunkText:
    """Tests for plain text semantic chunking."""

    def test_single_paragraph(self) -> None:
        content = (
            "This is a single paragraph of text that is long enough to not be merged."
        )
        chunks = chunk_text(content, max_chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].content == content
        assert chunks[0].heading_path == "Paragraph 1"

    def test_multiple_paragraphs(self) -> None:
        content = """This is the first paragraph with enough content to stand alone.

This is the second paragraph, also with sufficient length to be separate.

This is the third paragraph, meeting the minimum size requirement."""
        chunks = chunk_text(content, max_chunk_size=1000)

        assert len(chunks) == 3
        assert chunks[0].heading_path == "Paragraph 1"
        assert chunks[1].heading_path == "Paragraph 2"
        assert chunks[2].heading_path == "Paragraph 3"

    def test_short_title_merged_with_next_paragraph(self) -> None:
        content = """Short Title

This is the actual content that follows the title and should be merged with it."""
        chunks = chunk_text(content, max_chunk_size=1000)

        assert len(chunks) == 1
        assert "Short Title" in chunks[0].content
        assert "actual content" in chunks[0].content
        assert chunks[0].heading_path == "Paragraph 1"

    def test_paragraph_exceeds_limit_excluded(self) -> None:
        long_para = "X" * 500
        content = f"""This paragraph is long enough to stand alone by itself.

{long_para}

Another paragraph that is also long enough to stand alone."""

        chunks = chunk_text(content, max_chunk_size=100)

        assert len(chunks) == 2
        assert "long enough to stand alone" in chunks[0].content
        assert "also long enough" in chunks[1].content

    def test_empty_content(self) -> None:
        chunks = chunk_text("", max_chunk_size=1000)
        assert chunks == []

    def test_only_whitespace(self) -> None:
        chunks = chunk_text("   \n\n   \n   ", max_chunk_size=1000)
        assert chunks == []

    def test_preserves_positions(self) -> None:
        content = "This is the first paragraph with more than enough text here.\n\nThis is the second paragraph with more than enough text here."
        chunks = chunk_text(content, max_chunk_size=1000)

        assert len(chunks) == 2
        for chunk in chunks:
            extracted = content[chunk.start_position : chunk.end_position]
            assert extracted == chunk.content


class TestChunkDocument:
    """Tests for the unified document chunking interface."""

    def test_markdown_doc_type(self) -> None:
        content = "# Test\n\nContent"
        chunks = chunk_document(content, DocType.MARKDOWN, max_chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].heading_path == "Test"

    def test_text_doc_type(self) -> None:
        content = "This is the first paragraph with enough content to be standalone.\n\nThis is the second paragraph, also with sufficient content."
        chunks = chunk_document(content, DocType.TEXT, max_chunk_size=1000)

        assert len(chunks) == 2
        assert chunks[0].heading_path == "Paragraph 1"

    def test_pdf_treated_as_markdown(self) -> None:
        content = "# PDF Heading\n\nPDF content after conversion."
        chunks = chunk_document(content, DocType.PDF, max_chunk_size=1000)

        assert len(chunks) == 1
        assert chunks[0].heading_path == "PDF Heading"


class TestRealWorldExamples:
    """Tests using realistic document structures."""

    def test_cat_care_guide_small_sections(self) -> None:
        """A document with small level 1 sections that all fit."""
        content = """# Persian Cat Care

Persian cats need daily grooming due to their long coats.

# Feeding Tips

Feed high-quality cat food twice daily.

# Health Checks

Regular vet visits are important.
"""
        chunks = chunk_markdown(content, max_chunk_size=500)

        assert len(chunks) == 3
        paths = [c.heading_path for c in chunks]
        assert "Persian Cat Care" in paths
        assert "Feeding Tips" in paths
        assert "Health Checks" in paths

    def test_comprehensive_guide_needs_level2(self) -> None:
        """A document where level 1 sections are too large."""
        content = """# Complete Guide to Maine Coon Cats

Maine Coons are wonderful cats known for their size and personality.

## Physical Characteristics

Maine Coons are large cats, typically weighing 10-25 pounds. They have distinctive tufted ears, bushy tails, and water-resistant coats. Their eyes are large and expressive, usually green or gold.

## Personality

Despite their size, Maine Coons are gentle giants. They are friendly, playful, and get along well with children and other pets. They often follow their owners around and enjoy interactive play.

## Care Requirements

Maine Coons need regular grooming due to their long coats. Brush them several times per week to prevent matting. They also need proper nutrition and regular veterinary check-ups.
"""
        chunks = chunk_markdown(content, max_chunk_size=400)

        assert len(chunks) == 3
        assert all(
            "Complete Guide to Maine Coon Cats" in c.heading_path for c in chunks
        )
        assert any("Physical Characteristics" in c.heading_path for c in chunks)
        assert any("Personality" in c.heading_path for c in chunks)
        assert any("Care Requirements" in c.heading_path for c in chunks)

    def test_text_file_with_varying_paragraphs(self) -> None:
        """A text file with paragraphs of varying sizes."""
        content = """The Art of Puppy Cuddles

There's nothing quite like holding a warm, sleepy puppy. Their soft fur and gentle breathing create moments of pure peace.

Puppies sleep a lot - up to 18 hours per day. This is normal and important for their development. During sleep, they process new experiences and grow.

Short note.

Always supervise young children with puppies to ensure safe interactions for both."""

        chunks = chunk_text(content, max_chunk_size=300)

        assert len(chunks) >= 2
        assert "Puppy Cuddles" in chunks[0].content
        assert "nothing quite like holding" in chunks[0].content


class TestCreateVectorChunks:
    """Tests for fixed-size overlapping vector chunking."""

    def test_empty_content(self) -> None:
        chunks = create_vector_chunks(
            "", chunk_size=100, overlap_size=20, semantic_chunks=[]
        )
        assert chunks == []

    def test_content_smaller_than_chunk_size(self) -> None:
        content = "Short content"
        chunks = create_vector_chunks(
            content, chunk_size=100, overlap_size=20, semantic_chunks=[]
        )

        assert len(chunks) == 1
        assert chunks[0].content == content
        assert chunks[0].start_position == 0
        assert chunks[0].end_position == len(content)

    def test_creates_overlapping_chunks(self) -> None:
        content = "A" * 250
        chunks = create_vector_chunks(
            content, chunk_size=100, overlap_size=20, semantic_chunks=[]
        )

        assert len(chunks) == 3
        assert chunks[0].content == "A" * 100
        assert chunks[0].start_position == 0
        assert chunks[0].end_position == 100

        assert chunks[1].start_position == 80
        assert chunks[1].end_position == 180

        assert chunks[2].start_position == 160
        assert chunks[2].end_position == 250

    def test_links_to_parent_semantic_chunks(self) -> None:
        content = "A" * 200
        id1 = UUID("00000000-0000-0000-0000-000000000001")
        id2 = UUID("00000000-0000-0000-0000-000000000002")

        semantic_chunks = [
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 1",
                start_position=0,
                end_position=100,
                id=id1,
            ),
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 2",
                start_position=100,
                end_position=200,
                id=id2,
            ),
        ]

        chunks = create_vector_chunks(
            content, chunk_size=50, overlap_size=10, semantic_chunks=semantic_chunks
        )

        chunk_at_boundary = next(c for c in chunks if c.start_position == 80)
        assert id1 in chunk_at_boundary.semantic_chunk_ids
        assert id2 in chunk_at_boundary.semantic_chunk_ids

    def test_vector_chunk_spans_multiple_semantic_chunks(self) -> None:
        content = "A" * 300
        id1 = UUID("00000000-0000-0000-0000-000000000001")
        id2 = UUID("00000000-0000-0000-0000-000000000002")
        id3 = UUID("00000000-0000-0000-0000-000000000003")

        semantic_chunks = [
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 1",
                start_position=0,
                end_position=100,
                id=id1,
            ),
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 2",
                start_position=100,
                end_position=200,
                id=id2,
            ),
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 3",
                start_position=200,
                end_position=300,
                id=id3,
            ),
        ]

        chunks = create_vector_chunks(
            content, chunk_size=150, overlap_size=50, semantic_chunks=semantic_chunks
        )

        first_chunk = chunks[0]
        assert id1 in first_chunk.semantic_chunk_ids
        assert id2 in first_chunk.semantic_chunk_ids
        assert id3 not in first_chunk.semantic_chunk_ids

    def test_no_semantic_chunks_available(self) -> None:
        content = "Some text content"
        chunks = create_vector_chunks(
            content, chunk_size=100, overlap_size=20, semantic_chunks=[]
        )

        assert len(chunks) == 1
        assert chunks[0].semantic_chunk_ids == []

    def test_vector_chunk_outside_all_semantic_chunks(self) -> None:
        content = "Preamble text\n\n# Heading\n\nContent under heading"
        id1 = UUID("00000000-0000-0000-0000-000000000001")

        semantic_chunks = [
            StoredSemanticChunk(
                content="# Heading\n\nContent under heading",
                heading_path="Heading",
                start_position=15,
                end_position=len(content),
                id=id1,
            ),
        ]

        chunks = create_vector_chunks(
            content, chunk_size=10, overlap_size=2, semantic_chunks=semantic_chunks
        )

        first_chunk = chunks[0]
        assert first_chunk.start_position == 0
        assert first_chunk.end_position == 10
        assert first_chunk.semantic_chunk_ids == []

    def test_exact_boundary_no_overlap(self) -> None:
        content = "A" * 200
        id1 = UUID("00000000-0000-0000-0000-000000000001")
        id2 = UUID("00000000-0000-0000-0000-000000000002")

        semantic_chunks = [
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 1",
                start_position=0,
                end_position=100,
                id=id1,
            ),
            StoredSemanticChunk(
                content="A" * 100,
                heading_path="Section 2",
                start_position=100,
                end_position=200,
                id=id2,
            ),
        ]

        chunks = create_vector_chunks(
            content, chunk_size=100, overlap_size=0, semantic_chunks=semantic_chunks
        )

        assert len(chunks) == 2
        assert chunks[0].semantic_chunk_ids == [id1]
        assert chunks[1].semantic_chunk_ids == [id2]
