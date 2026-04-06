import pytest
from mcp.server.fastmcp import FastMCP

from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.exceptions import ValidationError
from struct_mark_docs_mcp.frontmatter_io import read_file, write_file
from struct_mark_docs_mcp.models import FileFrontmatter
from struct_mark_docs_mcp.ops.header_ops import sync_header
from struct_mark_docs_mcp.ops.list_ops import list_files
from struct_mark_docs_mcp.ops.pending_ops import get_pending_actions
from struct_mark_docs_mcp.ops.section_ops import add_section, read_section, remove_section, write_section
from struct_mark_docs_mcp.server import create_server


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


def test_create_server_smoke():
    server = create_server()
    assert isinstance(server, FastMCP)


# ---------------------------------------------------------------------------
# Auto-initialisation of bare .md files
# ---------------------------------------------------------------------------


def test_bare_file_auto_initialised(tmp_path):
    bare = tmp_path / "my_doc.md"
    bare.write_text("Some content without frontmatter.\n", encoding="utf-8")

    fm, body = read_file(tmp_path, "my_doc.md")

    assert fm.title == "my_doc"
    assert body.strip() == "Some content without frontmatter."
    # File on disk now has frontmatter
    content = bare.read_text(encoding="utf-8")
    assert content.startswith("---")
    assert "title: my_doc" in content


def test_bare_file_with_spaces_in_stem(tmp_path):
    bare = tmp_path / "My Doc.md"
    bare.write_text("Content.\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        read_file(tmp_path, "My Doc.md")


def test_bare_file_list_files_auto_inits(tmp_path):
    (tmp_path / "bare.md").write_text("Hello world.\n", encoding="utf-8")

    result = list_files(tmp_path, DocsConfig())

    assert "bare.md" in result
    # File should now have frontmatter
    content = (tmp_path / "bare.md").read_text(encoding="utf-8")
    assert content.startswith("---")


def test_read_file_idempotent_after_init(tmp_path):
    bare = tmp_path / "doc.md"
    bare.write_text("Content.\n", encoding="utf-8")

    fm1, body1 = read_file(tmp_path, "doc.md")
    fm2, body2 = read_file(tmp_path, "doc.md")

    assert fm1.title == fm2.title
    assert body1 == body2


# ---------------------------------------------------------------------------
# Full workflow: sync_header → get_pending_actions
# ---------------------------------------------------------------------------


def test_full_workflow_sync_then_pending(tmp_path):
    config = DocsConfig()
    (tmp_path / "guide.md").write_text(
        "# Introduction\n\nThis is the intro.\n\n# Conclusion\n\nFinal words.\n",
        encoding="utf-8",
    )

    sync_header(tmp_path, config, "guide.md")

    pending = get_pending_actions(tmp_path, config)
    assert "guide.md" in pending
    assert "missing_abstract" not in pending  # type label not in output
    assert "write abstract" in pending


def test_full_workflow_abstract_clears_pending(tmp_path):
    config = DocsConfig()
    fm = FileFrontmatter(title="doc", abstract="A" * 100)
    write_file(tmp_path, "doc.md", fm, "")

    pending = get_pending_actions(tmp_path, config)
    assert "No pending actions" in pending


# ---------------------------------------------------------------------------
# Full workflow: refs lifecycle
# ---------------------------------------------------------------------------


def test_full_workflow_refs_lifecycle(tmp_path):
    config = DocsConfig()
    fm_other = FileFrontmatter(title="other", abstract="Other doc.")
    write_file(tmp_path, "other.md", fm_other, "")
    # doc.md links to other.md
    (tmp_path / "doc.md").write_text(
        "See [other](other.md) for details.\n", encoding="utf-8"
    )

    sync_header(tmp_path, config, "doc.md")

    fm_doc, _ = read_file(tmp_path, "doc.md")
    assert "other" in fm_doc.refs
    fm_other2, _ = read_file(tmp_path, "other.md")
    assert "doc" in fm_other2.back_refs

    # Remove link and re-sync
    write_file(tmp_path, "doc.md", fm_doc, "No links anymore.\n")
    sync_header(tmp_path, config, "doc.md")

    fm_doc3, _ = read_file(tmp_path, "doc.md")
    assert "other" not in fm_doc3.refs
    fm_other3, _ = read_file(tmp_path, "other.md")
    assert "doc" not in fm_other3.back_refs


# ---------------------------------------------------------------------------
# Full workflow: section CRUD
# ---------------------------------------------------------------------------


def test_full_workflow_section_crud(tmp_path):
    config = DocsConfig()
    fm = FileFrontmatter(title="doc", abstract="A doc.")
    write_file(tmp_path, "doc.md", fm, "")

    add_section(tmp_path, config, "doc.md", "Overview")
    add_section(tmp_path, config, "doc.md", "Details")

    write_section(tmp_path, config, "doc.md", "Overview", "Overview body text.")

    content = read_section(tmp_path, "doc.md", "Overview")
    assert "Overview body text." in content

    remove_section(tmp_path, config, "doc.md", "Details")

    fm_after, body = read_file(tmp_path, "doc.md")
    titles = [s.title for s in fm_after.toc]
    assert "Overview" in titles
    assert "Details" not in titles
