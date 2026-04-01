import pytest

from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.exceptions import SectionNotFoundError, ValidationError
from struct_mark_docs_mcp.frontmatter_io import read_file, write_file
from struct_mark_docs_mcp.models import (
    FileFrontmatter,
    SectionMeta,
    SubsectionMeta,
    SubsubsectionMeta,
)
from struct_mark_docs_mcp.ops.abstract_ops import update_abstract


def _make_deep_file(tmp_path):
    """Write a file with section → subsection → subsubsection."""
    fm = FileFrontmatter(
        title="doc",
        toc=[
            SectionMeta(
                title="Intro",
                wc=0,
                subsections=[
                    SubsectionMeta(
                        title="Background",
                        wc=0,
                        subsubsections=[
                            SubsubsectionMeta(title="History", wc=0),
                        ],
                    )
                ],
            )
        ],
    )
    write_file(tmp_path, "doc.md", fm, "# Intro\n\n## Background\n\n### History\n\nText.")
    return fm


def test_file_level_abstract(tmp_path):
    fm = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm, "")
    update_abstract(tmp_path, DocsConfig(), "doc.md", "Top-level abstract.")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.abstract == "Top-level abstract."


def test_section_level_abstract(tmp_path):
    _make_deep_file(tmp_path)
    update_abstract(tmp_path, DocsConfig(), "doc.md", "Section abstract.", "Intro")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.toc[0].abstract == "Section abstract."


def test_subsection_level_abstract(tmp_path):
    _make_deep_file(tmp_path)
    update_abstract(tmp_path, DocsConfig(), "doc.md", "Sub abstract.", "Intro/Background")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.toc[0].subsections[0].abstract == "Sub abstract."


def test_subsubsection_level_abstract(tmp_path):
    _make_deep_file(tmp_path)
    update_abstract(
        tmp_path, DocsConfig(), "doc.md", "Subsub abstract.", "Intro/Background/History"
    )
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.toc[0].subsections[0].subsubsections[0].abstract == "Subsub abstract."


def test_snake_equivalence_in_path(tmp_path):
    """Path matching uses snake equivalence, not exact string match."""
    fm = FileFrontmatter(
        title="doc",
        toc=[SectionMeta(title="My Section", wc=0)],
    )
    write_file(tmp_path, "doc.md", fm, "# My Section\n\nContent.")
    # "my section" snake → "my_section", same as to_snake("My Section")
    update_abstract(tmp_path, DocsConfig(), "doc.md", "Snake match.", "my section")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.toc[0].abstract == "Snake match."


def test_overlimit_file_abstract_rejected(tmp_path):
    fm = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm, "")
    too_long = "x" * 381
    with pytest.raises(ValidationError):
        update_abstract(tmp_path, DocsConfig(), "doc.md", too_long)


def test_overlimit_section_abstract_rejected(tmp_path):
    _make_deep_file(tmp_path)
    too_long = "x" * 289
    with pytest.raises(ValidationError):
        update_abstract(tmp_path, DocsConfig(), "doc.md", too_long, "Intro")


def test_section_not_found(tmp_path):
    fm = FileFrontmatter(title="doc", toc=[SectionMeta(title="Intro", wc=0)])
    write_file(tmp_path, "doc.md", fm, "# Intro\n\nContent.")
    with pytest.raises(SectionNotFoundError):
        update_abstract(tmp_path, DocsConfig(), "doc.md", "Nope.", "Nonexistent")


def test_subsection_not_found(tmp_path):
    _make_deep_file(tmp_path)
    with pytest.raises(SectionNotFoundError):
        update_abstract(tmp_path, DocsConfig(), "doc.md", "Nope.", "Intro/Nonexistent")


def test_returns_action_string(tmp_path):
    fm = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm, "")
    result = update_abstract(tmp_path, DocsConfig(), "doc.md", "Abstract.")
    assert result.startswith("ACTION:")
    assert "NEXT_STEPS" in result
