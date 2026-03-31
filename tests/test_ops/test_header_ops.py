from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.frontmatter_io import read_file, write_file
from struct_mark_docs_mcp.models import FileFrontmatter, SectionMeta
from struct_mark_docs_mcp.ops.header_ops import read_header, scan_refs, sync_header


def test_read_header_returns_yaml(tmp_path):
    fm = FileFrontmatter(title="doc", abstract="An abstract.", wc=10)
    write_file(tmp_path, "doc.md", fm, "# Intro\n\nHello.")
    result = read_header(tmp_path, "doc.md")
    assert "title:" in result
    assert "abstract:" in result
    assert "wc:" in result


def test_scan_refs_extracts_md_links(tmp_path):
    body = "See [Foo](foo.md) and [Bar](bar.md) for more."
    refs = scan_refs(body)
    assert refs == ["foo", "bar"]


def test_scan_refs_ignores_non_md_links():
    body = "Visit [site](https://example.com) and [doc](notes.md)."
    refs = scan_refs(body)
    assert refs == ["notes"]


def test_scan_refs_deduplicates():
    body = "[A](foo.md) and again [B](foo.md)."
    refs = scan_refs(body)
    assert refs == ["foo"]


def test_scan_refs_strips_anchor():
    body = "[Section](guide.md#section-one)"
    refs = scan_refs(body)
    assert refs == ["guide"]


def test_scan_refs_empty():
    assert scan_refs("No links here.") == []


def test_sync_header_recomputes_wc(tmp_path):
    fm = FileFrontmatter(title="doc", wc=0)
    write_file(tmp_path, "doc.md", fm, "one two three four five")
    sync_header(tmp_path, DocsConfig(), "doc.md")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.wc == 5


def test_sync_header_rebuilds_toc(tmp_path):
    fm = FileFrontmatter(title="doc", wc=0)
    write_file(tmp_path, "doc.md", fm, "# Introduction\n\nHello world.\n\n## Details\n\nMore text.")
    sync_header(tmp_path, DocsConfig(), "doc.md")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert len(fm2.toc) == 1
    assert fm2.toc[0].title == "Introduction"
    assert len(fm2.toc[0].subsections) == 1
    assert fm2.toc[0].subsections[0].title == "Details"


def test_sync_header_preserves_abstracts(tmp_path):
    fm = FileFrontmatter(
        title="doc",
        toc=[SectionMeta(title="Introduction", abstract="Existing abstract.", wc=0)],
    )
    write_file(tmp_path, "doc.md", fm, "# Introduction\n\nNew content here.")
    sync_header(tmp_path, DocsConfig(), "doc.md")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert fm2.toc[0].abstract == "Existing abstract."


def test_sync_header_updates_refs(tmp_path):
    fm = FileFrontmatter(title="doc", refs=[])
    write_file(tmp_path, "doc.md", fm, "See [other](other.md) for details.")
    sync_header(tmp_path, DocsConfig(), "doc.md")
    fm2, _ = read_file(tmp_path, "doc.md")
    assert "other" in fm2.refs


def test_sync_header_does_not_touch_other_files(tmp_path):
    fm_a = FileFrontmatter(title="a", back_refs=["b"])
    write_file(tmp_path, "a.md", fm_a, "No links.")
    fm_b = FileFrontmatter(title="b", back_refs=[])
    write_file(tmp_path, "b.md", fm_b, "")

    sync_header(tmp_path, DocsConfig(), "b.md")

    fm_a2, _ = read_file(tmp_path, "a.md")
    assert fm_a2.back_refs == ["b"]  # unchanged


def test_sync_header_returns_action_string(tmp_path):
    fm = FileFrontmatter(title="doc")
    write_file(tmp_path, "doc.md", fm, "")
    result = sync_header(tmp_path, DocsConfig(), "doc.md")
    assert result.startswith("ACTION:")
    assert "NEXT_STEPS:" in result
