import pytest

from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.exceptions import (
    SectionNotFoundError,
    ValidationError,
)
from struct_mark_docs_mcp.frontmatter_io import read_file
from struct_mark_docs_mcp.ops.abstract_ops import update_abstract


class TestAbstractOps:
    @pytest.fixture
    def docs_dir(self, tmp_path):
        return tmp_path

    @pytest.fixture
    def config(self):
        return DocsConfig()

    @pytest.fixture
    def sample_file(self, docs_dir):
        # Create a sample markdown file with complete TOC structure
        content = """---
title: sample_file
abstract: Original file abstract
wc: 50
toc:
  - title: Section One
    abstract: Original section abstract
    wc: 20
    subsections:
      - title: Subsection One
        abstract: Original subsection abstract
        wc: 10
        subsubsections:
          - title: Subsubsection One
            abstract: Original subsubsection abstract
            wc: 5
  - title: Section Two
    abstract: ""
    wc: 15
refs: []
back_refs: []
---

# Section One

Content for section one.

## Subsection One

Content for subsection one.

### Subsubsection One

Content for subsubsection one.

# Section Two

Content for section two.
"""
        file_path = docs_dir / "sample_file.md"
        file_path.write_text(content)
        return "sample_file.md"

    def test_file_level_abstract_update(self, docs_dir, config, sample_file):
        result = update_abstract(docs_dir, config, sample_file, "Updated file abstract")

        assert "ACTION: updated file-level abstract for sample_file.md" in result
        assert "run get_pending_actions to check for remaining tasks" in result

        # Verify change
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.abstract == "Updated file abstract"

    def test_section_level_abstract_update(self, docs_dir, config, sample_file):
        result = update_abstract(
            docs_dir, config, sample_file, "Updated section abstract", "Section One"
        )

        assert (
            "ACTION: updated abstract for section 'Section One' in sample_file.md"
            in result
        )
        # Should suggest updating file-level abstract for top-level section
        assert "update file-level abstract for sample_file.md" in result
        assert "run get_pending_actions to check for remaining tasks" in result

        # Verify change
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].abstract == "Updated section abstract"

    def test_subsection_level_abstract_update(self, docs_dir, config, sample_file):
        result = update_abstract(
            docs_dir,
            config,
            sample_file,
            "Updated subsection abstract",
            "Section One/Subsection One",
        )

        assert (
            "ACTION: updated abstract for section 'Section One/Subsection One' in sample_file.md"
            in result
        )
        # Should suggest updating parent section
        assert "update abstract for 'Section One' in sample_file.md" in result
        assert "run get_pending_actions to check for remaining tasks" in result

        # Verify change
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].subsections[0].abstract == "Updated subsection abstract"

    def test_subsubsection_level_abstract_update(self, docs_dir, config, sample_file):
        result = update_abstract(
            docs_dir,
            config,
            sample_file,
            "Updated subsubsection abstract",
            "Section One/Subsection One/Subsubsection One",
        )

        assert (
            "ACTION: updated abstract for section 'Section One/Subsection One/Subsubsection One' in sample_file.md"
            in result
        )

        # Verify change
        fm, _ = read_file(docs_dir, sample_file)
        assert (
            fm.toc[0].subsections[0].subsubsections[0].abstract
            == "Updated subsubsection abstract"
        )

    def test_abstract_length_validation(self, docs_dir, config, sample_file):
        # Test file-level limit
        with pytest.raises(ValidationError):
            update_abstract(docs_dir, config, sample_file, "x" * 400)  # Over 380 limit

        # Test section-level limit
        with pytest.raises(ValidationError):
            update_abstract(
                docs_dir, config, sample_file, "x" * 300, "Section One"
            )  # Over 288 limit

        # Test exact limit boundary (should pass)
        exact_file_limit = "x" * 380  # Exactly at file limit
        result = update_abstract(docs_dir, config, sample_file, exact_file_limit)
        assert "ACTION: updated file-level abstract" in result

        exact_section_limit = "x" * 288  # Exactly at section limit
        result = update_abstract(
            docs_dir, config, sample_file, exact_section_limit, "Section One"
        )
        assert "ACTION: updated abstract for section" in result

    def test_nonexistent_section(self, docs_dir, config, sample_file):
        with pytest.raises(SectionNotFoundError):
            update_abstract(
                docs_dir, config, sample_file, "abstract", "Nonexistent Section"
            )

    def test_snake_case_path_matching(self, docs_dir, config, sample_file):
        # Test with different capitalization and spacing
        result = update_abstract(
            docs_dir,
            config,
            sample_file,
            "Snake case test",
            "section-one/subsection-one",
        )

        assert (
            "ACTION: updated abstract for section 'section-one/subsection-one'"
            in result
        )

        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].subsections[0].abstract == "Snake case test"

    def test_whitespace_handling(self, docs_dir, config, sample_file):
        # Test abstract with various whitespace
        abstract_with_whitespace = (
            "  Abstract with   extra   spaces  \n  and newlines  "
        )
        update_abstract(docs_dir, config, sample_file, abstract_with_whitespace)

        # Should preserve whitespace as provided (user intent)
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.abstract == abstract_with_whitespace

    def test_leading_trailing_slashes_level_calculation(self, docs_dir, config, sample_file):
        """Test that level calculation correctly filters empty strings from slashes"""
        
        # Test leading and trailing slashes: "/Section One/" should be level 1, not 3
        result = update_abstract(
            docs_dir, config, sample_file, "Test abstract", "/Section One/"
        )
        assert "ACTION: updated abstract for section '/Section One/'" in result
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].abstract == "Test abstract"
        
        # Test trailing slash only: "Section One/" should be level 1
        result = update_abstract(
            docs_dir, config, sample_file, "Test abstract 2", "Section One/"
        )
        assert "ACTION: updated abstract for section 'Section One/'" in result
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].abstract == "Test abstract 2"
        
        # Test leading slash only: "/Section One" should be level 1
        result = update_abstract(
            docs_dir, config, sample_file, "Test abstract 3", "/Section One"
        )
        assert "ACTION: updated abstract for section '/Section One'" in result
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].abstract == "Test abstract 3"
        
        # Test no slashes: "Section One" should be level 1 (baseline)
        result = update_abstract(
            docs_dir, config, sample_file, "Test abstract 4", "Section One"
        )
        assert "ACTION: updated abstract for section 'Section One'" in result
        fm, _ = read_file(docs_dir, sample_file)
        assert fm.toc[0].abstract == "Test abstract 4"

    def test_out_of_sync_empty_subsections_list(self, docs_dir, config, sample_file):
        """Test updating subsection abstract when parent has empty subsections list in TOC"""
        # First, modify the file to have empty subsections list in TOC but subsection exists in body
        fm, body = read_file(docs_dir, sample_file)
        
        # Clear the subsections list in TOC but keep the subsection in the body
        fm.toc[0].subsections = []
        from struct_mark_docs_mcp.frontmatter_io import write_file
        write_file(docs_dir, sample_file, fm, body)
        
        # Now try to update the subsection abstract - this should succeed with the fix
        # because the section exists in the body (find_section passes), but the TOC
        # traversal should attempt the recursive call even with empty list
        result = update_abstract(
            docs_dir,
            config,
            sample_file,
            "Updated subsection abstract in out-of-sync TOC",
            "Section One/Subsection One",
        )
        
        # Should succeed because section exists in body
        assert (
            "ACTION: updated abstract for section 'Section One/Subsection One' in sample_file.md"
            in result
        )
        
        # Verify the TOC model remains empty (no change) because there was nothing to traverse
        fm_updated, body_updated = read_file(docs_dir, sample_file)
        assert len(fm_updated.toc[0].subsections) == 0
        
        # But the section should still exist in the body (find_section would still find it)
        from struct_mark_docs_mcp.section_parser import parse_sections, find_section
        _, sections = parse_sections(body_updated)
        subsection = find_section(sections, "Section One/Subsection One")
        assert subsection.title == "Subsection One"
