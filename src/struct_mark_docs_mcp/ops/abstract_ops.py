from pathlib import Path

from ..config import DocsConfig
from ..frontmatter_io import read_file, write_file
from ..section_parser import parse_sections, find_section
from ..validation import check_abstract_length, to_snake


def update_abstract(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    abstract: str,
    section_path: str | None = None,
) -> str:
    """Update abstract for file or specific section.

    Args:
        docs_dir: Documentation directory path
        config: Documentation configuration
        filename: Target markdown file
        abstract: New abstract content
        section_path: Optional section path (None = file-level abstract)

    Returns:
        Standardized ACTION/NEXT_STEPS response string

    Raises:
        DocsFileNotFoundError: If file doesn't exist
        SectionNotFoundError: If section_path doesn't exist in file
        ValidationError: If abstract fails validation
    """
    # Read current file
    fm, body = read_file(docs_dir, filename)

    # Determine validation level and update appropriate abstract
    if section_path is None:
        # File-level abstract update
        level = 0
        check_abstract_length(abstract, level, config)

        fm.abstract = abstract

        action = f"updated file-level abstract for {filename}"

    else:
        # Section-level abstract update - traverse TOC structure
        _, sections = parse_sections(body)
        find_section(sections, section_path)  # Verify section exists

        # Determine level from section path depth, filtering empty strings
        path_parts = [p.strip() for p in section_path.split("/") if p.strip()]
        level = len(path_parts)
        check_abstract_length(abstract, level, config)

        # Find and update the corresponding TOC entry using inline traversal
        def update_toc_recursive(toc_list, path_parts):
            if not path_parts:
                return toc_list

            current_part = path_parts[0]
            current_key = to_snake(current_part)

            for item in toc_list:
                item_key = to_snake(item.title)
                if item_key == current_key:
                    if len(path_parts) == 1:
                        item.abstract = abstract
                        return toc_list
                    else:
                        if hasattr(item, "subsections"):
                            item.subsections = update_toc_recursive(
                                item.subsections, path_parts[1:]
                            )
                        elif hasattr(item, "subsubsections"):
                            item.subsubsections = update_toc_recursive(
                                item.subsubsections, path_parts[1:]
                            )
                        return toc_list
            return toc_list

        fm.toc = update_toc_recursive(fm.toc, path_parts)

        action = f"updated abstract for section '{section_path}' in {filename}"

    # Write updated file
    write_file(docs_dir, filename, fm, body)

    # Generate context-aware next steps
    if section_path is None:
        next_steps = "  - run get_pending_actions to check for remaining tasks"
    else:
        parts = [p.strip() for p in section_path.split("/") if p.strip()]
        parent = "/".join(parts[:-1])
        parent_note = (
            f"  - update abstract for '{parent}' in {filename}\n" if parent
            else f"  - update file-level abstract for {filename}\n"
        )
        next_steps = parent_note + "  - run get_pending_actions to check for remaining tasks"

    return f"ACTION: {action}\nNEXT_STEPS:\n{next_steps}"
