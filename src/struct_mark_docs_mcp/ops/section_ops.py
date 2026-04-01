from pathlib import Path

from ..config import DocsConfig
from ..exceptions import SectionNotFoundError, ValidationError
from ..frontmatter_io import read_file, write_file
from ..section_parser import SectionBlock, find_section, parse_sections, render_sections
from ..validation import check_no_heading_injection, check_unique_section_title, to_snake
from .header_ops import sync_header


def read_section(docs_dir: Path, filename: str, section_path: str) -> str:
    """Return the full rendered section (heading + body + children)."""
    _, body = read_file(docs_dir, filename)
    _, sections = parse_sections(body)
    block = find_section(sections, section_path)
    return render_sections("", [block])


def write_section(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    section_path: str,
    content: str,
) -> str:
    """Replace a section's body-only (children preserved). Injection-checked."""
    check_no_heading_injection(content)

    fm, body = read_file(docs_dir, filename)
    preamble, sections = parse_sections(body)
    block = find_section(sections, section_path)

    stripped = content.strip()
    block.body = ("\n" + stripped + "\n\n") if stripped else "\n"

    write_file(docs_dir, filename, fm, render_sections(preamble, sections))
    sync_header(docs_dir, config, filename)

    parts = [p for p in section_path.split("/") if p]
    parent_note = (
        f"  - update abstract for {'/'.join(parts[:-1])!r} in {filename}\n"
        if len(parts) > 1
        else ""
    )
    return (
        f"ACTION: replaced body of section {section_path!r} in {filename}\n"
        "NEXT_STEPS:\n"
        f"  - update abstract for section {section_path!r} in {filename}\n"
        + parent_note
        + "  - run get_pending_actions to check for remaining tasks"
    )


def add_section(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    title: str,
    parent_path: str | None = None,
    position: int | None = None,
) -> str:
    """Add a section at root (level 1) or under a parent. Level derived from parent depth."""
    fm, body = read_file(docs_dir, filename)
    preamble, sections = parse_sections(body)

    if parent_path is None:
        parent_list = sections
        level = 1
    else:
        parent_block = find_section(sections, parent_path)
        parent_list = parent_block.children
        level = len([p for p in parent_path.split("/") if p]) + 1

    if level > 3:
        raise ValidationError("Cannot add sections deeper than level 3 (###)")

    check_unique_section_title(title, [b.title for b in parent_list])

    new_block = SectionBlock(level=level, title=title, body="\n")
    if position is None or position >= len(parent_list):
        parent_list.append(new_block)
    else:
        parent_list.insert(max(0, position), new_block)

    write_file(docs_dir, filename, fm, render_sections(preamble, sections))
    sync_header(docs_dir, config, filename)

    location = f"under {parent_path!r}" if parent_path else "at root"
    return (
        f"ACTION: added section {title!r} {location} in {filename}\n"
        "NEXT_STEPS:\n"
        f"  - write content for the new section {title!r}\n"
        f"  - update abstract for section {title!r} in {filename}\n"
        "  - run get_pending_actions to check for remaining tasks"
    )


def remove_section(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    section_path: str,
) -> str:
    """Remove a section and all its children."""
    fm, body = read_file(docs_dir, filename)
    preamble, sections = parse_sections(body)

    parts = [p for p in section_path.split("/") if p]
    if len(parts) == 1:
        parent_list = sections
    else:
        parent_block = find_section(sections, "/".join(parts[:-1]))
        parent_list = parent_block.children

    key = to_snake(parts[-1])
    idx = next(
        (i for i, b in enumerate(parent_list) if to_snake(b.title) == key), None
    )
    if idx is None:
        raise SectionNotFoundError(f"Section {parts[-1]!r} not found")
    parent_list.pop(idx)

    write_file(docs_dir, filename, fm, render_sections(preamble, sections))
    sync_header(docs_dir, config, filename)

    return (
        f"ACTION: removed section {section_path!r} from {filename}\n"
        "NEXT_STEPS:\n"
        "  - review any references to the removed section in other files\n"
        "  - run get_pending_actions to check for remaining tasks"
    )


def rename_section(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    section_path: str,
    new_title: str,
) -> str:
    """Rename a section heading and toc entry; flags that refs may need updating."""
    fm, body = read_file(docs_dir, filename)
    preamble, sections = parse_sections(body)

    parts = [p for p in section_path.split("/") if p]
    if len(parts) == 1:
        sibling_list = sections
    else:
        parent_block = find_section(sections, "/".join(parts[:-1]))
        sibling_list = parent_block.children

    block = find_section(sections, section_path)
    check_unique_section_title(
        new_title, [b.title for b in sibling_list if b is not block]
    )
    old_title = block.title
    block.title = new_title

    write_file(docs_dir, filename, fm, render_sections(preamble, sections))
    sync_header(docs_dir, config, filename)

    return (
        f"ACTION: renamed section {old_title!r} → {new_title!r} in {filename}\n"
        "NEXT_STEPS:\n"
        "  - check other files for references to the old section title\n"
        "  - run get_pending_actions to check for remaining tasks"
    )
