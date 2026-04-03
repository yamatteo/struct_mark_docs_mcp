import re
from dataclasses import dataclass, field

from .exceptions import SectionNotFoundError
from .models import SectionMeta, SubsectionMeta, SubsubsectionMeta
from .validation import to_snake

_HEADING_RE = re.compile(r"^(#{1,3}) (.+)$", re.MULTILINE)


@dataclass
class SectionBlock:
    level: int
    title: str
    body: str  # starts with \n (MULTILINE $ matches before \n, so m.end() lands on it)
    children: list["SectionBlock"] = field(default_factory=list)


def parse_sections(body: str) -> tuple[str, list[SectionBlock]]:
    """Parse ATX headings (levels 1-3) from body text into a section tree.

    Returns (preamble, sections) where preamble is text before the first heading.
    Section body text starts with the \\n that follows the heading line.
    """
    matches = list(_HEADING_RE.finditer(body))
    if not matches:
        return body, []

    preamble = body[: matches[0].start()]
    roots: list[SectionBlock] = []
    stack: list[SectionBlock] = []

    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        section_body = body[m.end() : body_end]

        block = SectionBlock(level=level, title=title, body=section_body)
        while stack and stack[-1].level >= level:
            stack.pop()
        if stack:
            stack[-1].children.append(block)
        else:
            roots.append(block)
        stack.append(block)

    return preamble, roots


def render_sections(preamble: str, sections: list[SectionBlock]) -> str:
    """Render a section tree back to markdown text.

    render_sections(*parse_sections(body)) == body for well-formed input.
    """

    def _render(block: SectionBlock) -> str:
        heading = "#" * block.level + " " + block.title
        return heading + block.body + "".join(_render(c) for c in block.children)

    return preamble + "".join(_render(s) for s in sections)


def find_section(sections: list[SectionBlock], path: str) -> SectionBlock:
    """Find a section by slash-separated display path using snake equivalence.

    Example: find_section(sections, "Introduction/Overview")
    Raises SectionNotFoundError if any path component is not found.
    """
    parts = [p for p in path.split("/") if p]
    current_list = sections
    current_block: SectionBlock | None = None

    for part in parts:
        key = to_snake(part)
        found = next((b for b in current_list if to_snake(b.title) == key), None)
        if found is None:
            raise SectionNotFoundError(f"Section {part!r} not found")
        current_block = found
        current_list = found.children

    if current_block is None:
        raise SectionNotFoundError("Empty section path")
    return current_block


def find_toc_section(
    toc: list[SectionMeta], path: str
) -> tuple[SectionMeta | SubsectionMeta | SubsubsectionMeta, int]:
    """Navigate TOC structure by snake-path, return (section, level).

    Args:
        toc: List of SectionMeta from FileFrontmatter.toc
        path: Slash-separated display path (e.g., "Introduction/Overview")

    Returns:
        Tuple of (found_section, level) where level is 1=section, 2=subsection, 3=subsubsection

    Raises:
        SectionNotFoundError: If path component not found at any level
    """
    # Import to_snake here to avoid circular imports
    from . import to_snake

    parts = [p for p in path.split("/") if p]
    if not parts:
        raise SectionNotFoundError("Empty section path")

    current_list = toc
    current_level = 1

    for i, part in enumerate(parts):
        if current_level > 3:
            raise SectionNotFoundError(f"Path too deep: {path}")

        key = to_snake(part)
        found = None

        if current_level == 1:
            found = next((s for s in current_list if to_snake(s.title) == key), None)
            if found:
                current_list = found.subsections
        elif current_level == 2:
            found = next((s for s in current_list if to_snake(s.title) == key), None)
            if found:
                current_list = found.subsubsections
        elif current_level == 3:
            found = next((s for s in current_list if to_snake(s.title) == key), None)

        if found is None:
            raise SectionNotFoundError(
                f"Section {part!r} not found at level {current_level}"
            )

        current_level += 1

    return found, current_level - 1


def update_toc_abstract(
    toc: list[SectionMeta], path: str, abstract: str
) -> list[SectionMeta]:
    """Update abstract in TOC structure, return modified TOC.

    Args:
        toc: List of SectionMeta from FileFrontmatter.toc
        path: Slash-separated display path
        abstract: New abstract content

    Returns:
        Modified TOC with updated abstract

    Raises:
        SectionNotFoundError: If path not found
    """
    # Create deep copy to avoid mutation issues
    import copy

    new_toc = copy.deepcopy(toc)

    section, level = find_toc_section(new_toc, path)
    section.abstract = abstract

    return new_toc


def section_path_to_key(path: str) -> list[str]:
    """Convert a slash-separated display path to a list of snake_case keys."""
    return [to_snake(p) for p in path.split("/") if p]
