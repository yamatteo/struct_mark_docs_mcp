import pytest

from struct_mark_docs_mcp.exceptions import DocsFileNotFoundError, ValidationError
from struct_mark_docs_mcp.frontmatter_io import read_file, resolve_path, write_file
from struct_mark_docs_mcp.models import FileFrontmatter, SectionMeta


def test_resolve_path_valid(tmp_path):
    path = resolve_path(tmp_path, "notes.md")
    assert path == (tmp_path / "notes.md").resolve()
    assert path.is_relative_to(tmp_path.resolve())


def test_resolve_path_traversal(tmp_path):
    with pytest.raises(DocsFileNotFoundError):
        resolve_path(tmp_path, "../outside.md")


def test_read_file_not_found(tmp_path):
    with pytest.raises(DocsFileNotFoundError):
        read_file(tmp_path, "missing.md")


def test_read_file_with_frontmatter(tmp_path):
    (tmp_path / "test.md").write_text(
        "---\ntitle: My Document\nabstract: A test.\nwc: 42\n---\n\nBody content here.\n",
        encoding="utf-8",
    )
    fm, body = read_file(tmp_path, "test.md")
    assert fm.title == "My Document"
    assert fm.abstract == "A test."
    assert fm.wc == 42
    assert "Body content here." in body


def test_read_file_no_frontmatter(tmp_path):
    (tmp_path / "my_doc.md").write_text("Plain text content.\n", encoding="utf-8")
    fm, body = read_file(tmp_path, "my_doc.md")
    assert fm.title == "my_doc"
    assert fm.wc == 0
    assert "Plain text" in body


def test_write_file_canonical_order(tmp_path):
    fm = FileFrontmatter(
        title="Test",
        abstract="An abstract.",
        wc=10,
        toc=[SectionMeta(title="Intro", abstract="Intro abstract.", wc=5)],
        refs=["other"],
        back_refs=["parent"],
    )
    write_file(tmp_path, "out.md", fm, "# Intro\n\nContent.\n")
    raw = (tmp_path / "out.md").read_text(encoding="utf-8")
    # Extract only the YAML block and check key order
    yaml_block = raw.split("---")[1]
    keys = [line.split(":")[0].strip() for line in yaml_block.splitlines() if ":" in line and not line.startswith(" ") and not line.startswith("-")]
    expected_order = ["title", "abstract", "wc", "toc", "refs", "back_refs"]
    assert keys == expected_order


def test_write_roundtrip(tmp_path):
    fm = FileFrontmatter(
        title="Round Trip",
        abstract="Testing roundtrip.",
        wc=99,
        toc=[SectionMeta(title="Section One", abstract="", wc=0)],
        refs=["other_doc"],
        back_refs=[],
    )
    body = "# Section One\n\nSome content.\n"
    write_file(tmp_path, "round.md", fm, body)
    fm2, body2 = read_file(tmp_path, "round.md")
    assert fm2 == fm
    assert body2 == body


# ---------------------------------------------------------------------------
# Snake case filename validation tests
# ---------------------------------------------------------------------------


def test_resolve_path_rejects_camel_case(tmp_path):
    with pytest.raises(ValidationError):
        resolve_path(tmp_path, "MyFile.md")


def test_resolve_path_rejects_spaces(tmp_path):
    with pytest.raises(ValidationError):
        resolve_path(tmp_path, "my file.md")


def test_resolve_path_rejects_empty_stem(tmp_path):
    with pytest.raises(ValidationError):
        resolve_path(tmp_path, ".md")


def test_resolve_path_accepts_snake_case(tmp_path):
    path = resolve_path(tmp_path, "my_file.md")
    assert path == (tmp_path / "my_file.md").resolve()


def test_read_file_rejects_invalid_filename(tmp_path):
    (tmp_path / "MyFile.md").write_text("# Content\n\nSome text.\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        read_file(tmp_path, "MyFile.md")


def test_write_file_rejects_invalid_filename(tmp_path):
    fm = FileFrontmatter(title="Test", abstract="Test abstract.", wc=5)
    with pytest.raises(ValidationError):
        write_file(tmp_path, "Bad File.md", fm, "Content")
