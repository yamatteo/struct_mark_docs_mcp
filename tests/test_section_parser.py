import pytest

from struct_mark_docs_mcp.exceptions import SectionNotFoundError
from struct_mark_docs_mcp.section_parser import (
    find_section,
    parse_sections,
    render_sections,
)


def test_parse_empty_body():
    preamble, sections = parse_sections("")
    assert preamble == ""
    assert sections == []


def test_parse_preamble_only():
    text = "Just some plain text.\nNo headings here.\n"
    preamble, sections = parse_sections(text)
    assert preamble == text
    assert sections == []


def test_parse_single_section():
    body = "# My Section\n\nBody text.\n"
    preamble, sections = parse_sections(body)
    assert preamble == ""
    assert len(sections) == 1
    s = sections[0]
    assert s.level == 1
    assert s.title == "My Section"
    assert s.body == "\n\nBody text.\n"
    assert s.children == []


def test_parse_nested_sections():
    body = "# Parent\n\nParent body.\n\n## Child\n\nChild body.\n\n### Grandchild\n\nGrandchild body.\n"
    preamble, sections = parse_sections(body)
    assert preamble == ""
    assert len(sections) == 1

    parent = sections[0]
    assert parent.level == 1
    assert parent.title == "Parent"
    assert len(parent.children) == 1

    child = parent.children[0]
    assert child.level == 2
    assert child.title == "Child"
    assert len(child.children) == 1

    grandchild = child.children[0]
    assert grandchild.level == 3
    assert grandchild.title == "Grandchild"
    assert grandchild.children == []


def test_parse_skipped_levels():
    body = "# Top\n\nTop body.\n\n### Deep\n\nDeep body.\n"
    preamble, sections = parse_sections(body)
    assert len(sections) == 1
    top = sections[0]
    assert top.level == 1
    assert len(top.children) == 1
    deep = top.children[0]
    assert deep.level == 3
    assert deep.children == []


def test_render_roundtrip():
    body = (
        "Preamble text.\n\n"
        "# Section One\n\nContent of section one.\n\n"
        "## Subsection\n\nSub content.\n\n"
        "# Section Two\n\nContent of section two.\n"
    )
    assert render_sections(*parse_sections(body)) == body


def test_find_section_top_level():
    _, sections = parse_sections("# Introduction\n\nText.\n")
    block = find_section(sections, "Introduction")
    assert block.title == "Introduction"


def test_find_section_snake_equivalence():
    _, sections = parse_sections("# My Section\n\nText.\n")
    assert find_section(sections, "My Section").title == "My Section"
    assert find_section(sections, "my_section").title == "My Section"
    assert find_section(sections, "MY_SECTION").title == "My Section"


def test_find_section_nested():
    body = "# Parent\n\nParent text.\n\n## Child\n\nChild text.\n"
    _, sections = parse_sections(body)
    block = find_section(sections, "Parent/Child")
    assert block.title == "Child"
    assert block.level == 2


def test_find_section_not_found():
    _, sections = parse_sections("# Introduction\n\nText.\n")
    with pytest.raises(SectionNotFoundError):
        find_section(sections, "Nonexistent")
    with pytest.raises(SectionNotFoundError):
        find_section(sections, "Introduction/Nonexistent")
