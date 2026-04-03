from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.frontmatter_io import read_file, write_file
from struct_mark_docs_mcp.models import FileFrontmatter
from struct_mark_docs_mcp.ops.header_ops import sync_header
from struct_mark_docs_mcp.ops.refs_ops import update_back_refs
from struct_mark_docs_mcp.ops.section_ops import write_section, remove_section


# ---------------------------------------------------------------------------
# update_back_refs — unit tests
# ---------------------------------------------------------------------------


def test_update_back_refs_adds_back_ref(tmp_path):
    fm_target = FileFrontmatter(title="target")
    write_file(tmp_path, "target.md", fm_target, "")
    fm_src = FileFrontmatter(title="source")
    write_file(tmp_path, "source.md", fm_src, "")

    update_back_refs(tmp_path, "source.md", [], ["target"])

    fm2, _ = read_file(tmp_path, "target.md")
    assert "source" in fm2.back_refs


def test_update_back_refs_removes_back_ref(tmp_path):
    fm_target = FileFrontmatter(title="target", back_refs=["source"])
    write_file(tmp_path, "target.md", fm_target, "")
    fm_src = FileFrontmatter(title="source")
    write_file(tmp_path, "source.md", fm_src, "")

    update_back_refs(tmp_path, "source.md", ["target"], [])

    fm2, _ = read_file(tmp_path, "target.md")
    assert "source" not in fm2.back_refs


def test_update_back_refs_is_idempotent(tmp_path):
    fm_target = FileFrontmatter(title="target", back_refs=["source"])
    write_file(tmp_path, "target.md", fm_target, "")
    fm_src = FileFrontmatter(title="source")
    write_file(tmp_path, "source.md", fm_src, "")

    # Adding again when already present — no duplicates
    update_back_refs(tmp_path, "source.md", [], ["target"])

    fm2, _ = read_file(tmp_path, "target.md")
    assert fm2.back_refs.count("source") == 1


def test_update_back_refs_ignores_missing_files(tmp_path):
    fm_src = FileFrontmatter(title="source")
    write_file(tmp_path, "source.md", fm_src, "")

    # "ghost" does not exist — should not raise
    update_back_refs(tmp_path, "source.md", [], ["ghost"])


def test_update_back_refs_ignores_self_reference(tmp_path):
    fm_src = FileFrontmatter(title="source")
    write_file(tmp_path, "source.md", fm_src, "")

    update_back_refs(tmp_path, "source.md", [], ["source"])

    fm2, _ = read_file(tmp_path, "source.md")
    assert "source" not in fm2.back_refs


# ---------------------------------------------------------------------------
# Integration through sync_header
# ---------------------------------------------------------------------------


def test_sync_header_adds_back_ref_to_target(tmp_path):
    fm_other = FileFrontmatter(title="other")
    write_file(tmp_path, "other.md", fm_other, "")
    fm_doc = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm_doc, "See [other](other.md).")

    sync_header(tmp_path, DocsConfig(), "doc.md")

    fm2, _ = read_file(tmp_path, "other.md")
    assert "doc" in fm2.back_refs


def test_sync_header_removes_back_ref_when_link_dropped(tmp_path):
    fm_other = FileFrontmatter(title="other", back_refs=["doc"])
    write_file(tmp_path, "other.md", fm_other, "")
    # doc.md already has "other" in its refs from a previous sync
    fm_doc = FileFrontmatter(title="doc", refs=["other"])
    write_file(tmp_path, "doc.md", fm_doc, "No links anymore.")

    sync_header(tmp_path, DocsConfig(), "doc.md")

    fm2, _ = read_file(tmp_path, "other.md")
    assert "doc" not in fm2.back_refs


# ---------------------------------------------------------------------------
# Integration through section operations
# ---------------------------------------------------------------------------


def test_write_section_updates_back_refs(tmp_path):
    fm_target = FileFrontmatter(title="target")
    write_file(tmp_path, "target.md", fm_target, "")
    fm_doc = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm_doc, "# Section\nOld content.")

    # Add a reference through section modification
    write_section(
        tmp_path, DocsConfig(), "doc.md", "Section", "See [target](target.md)."
    )

    fm_target2, _ = read_file(tmp_path, "target.md")
    assert "doc" in fm_target2.back_refs


def test_write_section_removes_back_refs(tmp_path):
    fm_target = FileFrontmatter(title="target", back_refs=["doc"])
    write_file(tmp_path, "target.md", fm_target, "")
    fm_doc = FileFrontmatter(title="doc", refs=["target"])
    write_file(tmp_path, "doc.md", fm_doc, "# Section\nSee [target](target.md).")

    # Remove the reference through section modification
    write_section(tmp_path, DocsConfig(), "doc.md", "Section", "No more links.")

    fm_target2, _ = read_file(tmp_path, "target.md")
    assert "doc" not in fm_target2.back_refs


def test_remove_section_cleans_up_refs(tmp_path):
    fm_target = FileFrontmatter(title="target")
    write_file(tmp_path, "target.md", fm_target, "")
    fm_doc = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm_doc, "# Section\nSee [target](target.md).")

    # Remove section containing the reference
    remove_section(tmp_path, DocsConfig(), "doc.md", "Section")

    fm_target2, _ = read_file(tmp_path, "target.md")
    assert "doc" not in fm_target2.back_refs
