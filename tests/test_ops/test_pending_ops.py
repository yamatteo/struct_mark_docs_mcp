from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.frontmatter_io import write_file
from struct_mark_docs_mcp.models import FileFrontmatter, SectionMeta, SubsectionMeta, SubsubsectionMeta
from struct_mark_docs_mcp.ops.pending_ops import get_pending_actions


def test_empty_directory(tmp_path):
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "No pending actions" in result


def test_clean_file_no_actions(tmp_path):
    fm = FileFrontmatter(title="doc", abstract="A" * 100)
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "No pending actions" in result


def test_missing_file_abstract(tmp_path):
    fm = FileFrontmatter(title="doc", abstract="")
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "missing_abstract" not in result  # type not in output
    assert "write abstract for doc.md" in result


def test_overlimit_file_abstract(tmp_path):
    config = DocsConfig()
    long_abstract = "x" * (config.abstract_limit(0) + 1)
    fm = FileFrontmatter(title="doc", abstract=long_abstract)
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "shorten abstract for doc.md" in result


def test_missing_section_abstract(tmp_path):
    fm = FileFrontmatter(
        title="doc",
        abstract="File abstract.",
        toc=[SectionMeta(title="Intro", wc=10)],
    )
    write_file(tmp_path, "doc.md", fm, "# Intro\n\nContent.\n")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "write abstract for 'Intro' in doc.md" in result


def test_section_over_wc_soft_limit(tmp_path):
    config = DocsConfig()
    fm = FileFrontmatter(
        title="doc",
        abstract="Abstract.",
        toc=[SectionMeta(title="Big", abstract="sec abstract.", wc=config.section_wc_soft_limit + 1)],
    )
    write_file(tmp_path, "doc.md", fm, "# Big\n\nContent.\n")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "over_wc" not in result  # type label not in output
    assert "section 'Big' in doc.md" in result
    assert "words" in result


def test_broken_ref(tmp_path):
    fm = FileFrontmatter(title="doc", abstract="Abstract.", refs=["ghost"])
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "broken ref 'ghost' in doc.md" in result


def test_stale_back_ref(tmp_path):
    fm = FileFrontmatter(title="doc", abstract="Abstract.", back_refs=["ghost"])
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "stale back_ref 'ghost' in doc.md" in result


def test_inconsistent_back_ref(tmp_path):
    # a.md claims b is a back_ref, but b.md doesn't list a in its refs
    fm_a = FileFrontmatter(title="a", abstract="Abstract.", back_refs=["b"])
    write_file(tmp_path, "a.md", fm_a, "")
    fm_b = FileFrontmatter(title="b", abstract="Abstract.", refs=[])
    write_file(tmp_path, "b.md", fm_b, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "back_ref 'b' in a.md" in result
    assert "sync_header on b.md" in result


def test_priority_broken_ref_before_missing_abstract(tmp_path):
    # broken ref + missing abstract — broken ref should appear first
    fm = FileFrontmatter(title="doc", abstract="", refs=["ghost"])
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert result.index("broken ref") < result.index("write abstract")


def test_nested_toc_all_levels_checked(tmp_path):
    fm = FileFrontmatter(
        title="doc",
        abstract="File abstract.",
        toc=[
            SectionMeta(
                title="Sec",
                abstract="sec abstract.",
                wc=10,
                subsections=[
                    SubsectionMeta(
                        title="Sub",
                        abstract="",  # missing
                        wc=5,
                        subsubsections=[
                            SubsubsectionMeta(title="Subsub", abstract="", wc=3),
                        ],
                    )
                ],
            )
        ],
    )
    write_file(tmp_path, "doc.md", fm, "")
    result = get_pending_actions(tmp_path, DocsConfig())
    assert "Sec/Sub" in result
    assert "Sec/Sub/Subsub" in result
