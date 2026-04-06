from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.frontmatter_io import write_file
from struct_mark_docs_mcp.models import FileFrontmatter
from struct_mark_docs_mcp.ops.list_ops import list_files


def test_list_files_empty_dir(tmp_path):
    assert list_files(tmp_path, DocsConfig()) == "(no markdown files found)"


def test_list_files_single_file(tmp_path):
    fm = FileFrontmatter(title="my_doc", abstract="Short abstract.", wc=5)
    write_file(tmp_path, "my_doc.md", fm, "Some content here.")
    result = list_files(tmp_path, DocsConfig())
    assert "my_doc.md" in result
    assert "wc=5" in result
    assert "abstract=ok" in result


def test_list_files_missing_abstract(tmp_path):
    fm = FileFrontmatter(title="bare", abstract="", wc=3)
    write_file(tmp_path, "bare.md", fm, "Hello world.")
    result = list_files(tmp_path, DocsConfig())
    assert "abstract=missing" in result


def test_list_files_overlimit_abstract(tmp_path):
    long_abstract = "x" * 400  # exceeds default limit of 380
    fm = FileFrontmatter(title="long_doc", abstract=long_abstract, wc=1)
    write_file(tmp_path, "long_doc.md", fm, "Content.")
    result = list_files(tmp_path, DocsConfig())
    assert "abstract=overlimit" in result


def test_list_files_multiple_sorted(tmp_path):
    for name in ["bravo.md", "alpha.md"]:
        fm = FileFrontmatter(title=name.removesuffix(".md"), abstract="ok", wc=0)
        write_file(tmp_path, name, fm, "")
    lines = list_files(tmp_path, DocsConfig()).splitlines()
    assert lines[0].startswith("alpha.md")
    assert lines[1].startswith("bravo.md")


def test_list_files_subdirectories(tmp_path):
    # Create subdirectories and files
    subdir = tmp_path / "subdir"
    nested = tmp_path / "subdir" / "nested"
    subdir.mkdir()
    nested.mkdir()
    
    # Create files in different locations
    fm_root = FileFrontmatter(title="root_doc", abstract="Root abstract", wc=10)
    fm_sub = FileFrontmatter(title="sub_doc", abstract="Sub abstract", wc=5)
    fm_nested = FileFrontmatter(title="nested_doc", abstract="Nested abstract", wc=3)
    
    write_file(tmp_path, "root_doc.md", fm_root, "Root content")
    write_file(tmp_path, "subdir/sub_doc.md", fm_sub, "Sub content")
    write_file(tmp_path, "subdir/nested/nested_doc.md", fm_nested, "Nested content")
    
    result = list_files(tmp_path, DocsConfig())
    lines = result.splitlines()
    
    # Check that all files are found with relative paths
    assert "root_doc.md" in result
    assert "subdir/sub_doc.md" in result
    assert "subdir/nested/nested_doc.md" in result
    
    # Check word counts and abstract status
    assert "wc=10" in lines[0]  # root_doc.md
    assert "wc=5" in result
    assert "wc=3" in result
    assert "abstract=ok" in result
