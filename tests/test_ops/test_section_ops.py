import pytest

from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.exceptions import (
    DuplicateSectionError,
    InjectionError,
    SectionNotFoundError,
    ValidationError,
)
from struct_mark_docs_mcp.frontmatter_io import read_file, write_file
from struct_mark_docs_mcp.models import FileFrontmatter, SectionMeta, SubsectionMeta
from struct_mark_docs_mcp.ops.section_ops import (
    add_section,
    read_section,
    remove_section,
    rename_section,
    write_section,
)


def _make_nested_file(tmp_path):
    """Write a file with section → subsection → sibling subsection."""
    fm = FileFrontmatter(
        title="doc",
        toc=[
            SectionMeta(
                title="Intro",
                wc=0,
                subsections=[
                    SubsectionMeta(title="Background", wc=0),
                    SubsectionMeta(title="Goals", wc=0),
                ],
            ),
            SectionMeta(title="Conclusion", wc=0),
        ],
    )
    body = (
        "# Intro\n\nIntro body.\n\n"
        "## Background\n\nBackground body.\n\n"
        "## Goals\n\nGoals body.\n\n"
        "# Conclusion\n\nConclusion body.\n"
    )
    write_file(tmp_path, "doc.md", fm, body)
    return fm


# ---------------------------------------------------------------------------
# read_section
# ---------------------------------------------------------------------------


def test_read_section_top_level(tmp_path):
    _make_nested_file(tmp_path)
    result = read_section(tmp_path, "doc.md", "Intro")
    assert "# Intro" in result
    assert "Intro body." in result


def test_read_section_nested(tmp_path):
    _make_nested_file(tmp_path)
    result = read_section(tmp_path, "doc.md", "Intro/Background")
    assert "## Background" in result
    assert "Background body." in result


def test_read_section_not_found(tmp_path):
    _make_nested_file(tmp_path)
    with pytest.raises(SectionNotFoundError):
        read_section(tmp_path, "doc.md", "Nonexistent")


# ---------------------------------------------------------------------------
# write_section
# ---------------------------------------------------------------------------


def test_write_section_replaces_body(tmp_path):
    _make_nested_file(tmp_path)
    write_section(tmp_path, DocsConfig(), "doc.md", "Intro", "New intro content.")
    result = read_section(tmp_path, "doc.md", "Intro")
    assert "New intro content." in result
    # Children preserved
    assert "## Background" in result


def test_write_section_injection_atx(tmp_path):
    _make_nested_file(tmp_path)
    with pytest.raises(InjectionError):
        write_section(tmp_path, DocsConfig(), "doc.md", "Intro", "# Injected heading")


def test_write_section_injection_setext(tmp_path):
    _make_nested_file(tmp_path)
    with pytest.raises(InjectionError):
        write_section(
            tmp_path, DocsConfig(), "doc.md", "Intro", "Fake heading\n==========="
        )


def test_write_section_updates_wc(tmp_path):
    _make_nested_file(tmp_path)
    write_section(tmp_path, DocsConfig(), "doc.md", "Intro", "one two three")
    fm, _ = read_file(tmp_path, "doc.md")
    # Total wc is recomputed by sync_header; at least not 0
    assert fm.wc > 0


def test_write_section_returns_action_string(tmp_path):
    _make_nested_file(tmp_path)
    result = write_section(tmp_path, DocsConfig(), "doc.md", "Intro", "Updated.")
    assert result.startswith("ACTION:")
    assert "NEXT_STEPS" in result


# ---------------------------------------------------------------------------
# add_section
# ---------------------------------------------------------------------------


def test_add_section_top_level(tmp_path):
    fm = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm, "# Existing\n\nContent.\n")
    add_section(tmp_path, DocsConfig(), "doc.md", "New Section")
    _, body = read_file(tmp_path, "doc.md")
    assert "# New Section" in body


def test_add_section_subsection(tmp_path):
    _make_nested_file(tmp_path)
    add_section(tmp_path, DocsConfig(), "doc.md", "New Sub", parent_path="Intro")
    _, body = read_file(tmp_path, "doc.md")
    assert "## New Sub" in body


def test_add_section_duplicate_rejected(tmp_path):
    _make_nested_file(tmp_path)
    with pytest.raises(DuplicateSectionError):
        add_section(tmp_path, DocsConfig(), "doc.md", "Intro")


def test_add_section_level4_rejected(tmp_path):
    """parent_path with 3 parts would create level 4 — rejected."""
    from struct_mark_docs_mcp.models import SubsubsectionMeta

    fm = FileFrontmatter(
        title="doc",
        toc=[
            SectionMeta(
                title="A",
                wc=0,
                subsections=[
                    SubsectionMeta(
                        title="B",
                        wc=0,
                        subsubsections=[SubsubsectionMeta(title="C", wc=0)],
                    )
                ],
            )
        ],
    )
    write_file(tmp_path, "doc.md", fm, "# A\n\n## B\n\n### C\n\nContent.\n")
    with pytest.raises(ValidationError):
        add_section(tmp_path, DocsConfig(), "doc.md", "D", parent_path="A/B/C")


# ---------------------------------------------------------------------------
# remove_section
# ---------------------------------------------------------------------------


def test_remove_section_top_level(tmp_path):
    _make_nested_file(tmp_path)
    remove_section(tmp_path, DocsConfig(), "doc.md", "Conclusion")
    _, body = read_file(tmp_path, "doc.md")
    assert "# Conclusion" not in body


def test_remove_section_leaves_siblings(tmp_path):
    _make_nested_file(tmp_path)
    remove_section(tmp_path, DocsConfig(), "doc.md", "Intro/Background")
    _, body = read_file(tmp_path, "doc.md")
    assert "## Background" not in body
    assert "## Goals" in body


def test_remove_section_not_found(tmp_path):
    _make_nested_file(tmp_path)
    with pytest.raises(SectionNotFoundError):
        remove_section(tmp_path, DocsConfig(), "doc.md", "Nonexistent")


# ---------------------------------------------------------------------------
# rename_section
# ---------------------------------------------------------------------------


def test_rename_section_updates_heading(tmp_path):
    _make_nested_file(tmp_path)
    rename_section(tmp_path, DocsConfig(), "doc.md", "Conclusion", "Summary")
    _, body = read_file(tmp_path, "doc.md")
    assert "# Summary" in body
    assert "# Conclusion" not in body


def test_rename_section_duplicate_rejected(tmp_path):
    _make_nested_file(tmp_path)
    with pytest.raises(DuplicateSectionError):
        rename_section(tmp_path, DocsConfig(), "doc.md", "Intro", "Conclusion")


def test_rename_section_returns_action_string(tmp_path):
    _make_nested_file(tmp_path)
    result = rename_section(tmp_path, DocsConfig(), "doc.md", "Conclusion", "Wrap Up")
    assert "NEXT_STEPS" in result
    assert "references" in result.lower() or "refs" in result.lower()
