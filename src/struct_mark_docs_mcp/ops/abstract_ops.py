from pathlib import Path

from ..config import DocsConfig
from ..exceptions import (
    SectionNotFoundError,
    TOCSyncError,
)
from ..frontmatter_io import read_file, write_file
from ..section_parser import find_toc_section, update_toc_abstract
from ..validation import (
    check_abstract_length,
    check_abstract_quality,
    validate_section_path,
)


def update_abstract(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    abstract: str,
    section_path: str | None = None,
) -> str:
    """Update abstract for file or specific section with full validation.

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
        SectionPathError: If section_path is invalid
        SectionNotFoundError: If section_path doesn't exist in file
        AbstractValidationError: If abstract fails validation
        TOCSyncError: If TOC is inconsistent with content
    """
    # Validate inputs
    if section_path is not None:
        validate_section_path(section_path)

    # Validate abstract quality
    check_abstract_quality(abstract)

    # Read current file
    fm, body = read_file(docs_dir, filename)

    # Determine validation level and update appropriate abstract
    if section_path is None:
        # File-level abstract update
        level = 0
        check_abstract_length(abstract, level, config)

        old_abstract = fm.abstract
        fm.abstract = abstract

        action = f"updated file-level abstract for {filename}"
        if old_abstract.strip() == abstract.strip():
            return f"ACTION: no change needed for {filename} (abstract already identical)\nNEXT_STEPS:\n  - abstract is up to date"

    else:
        # Section-level abstract update
        try:
            section, level = find_toc_section(fm.toc, section_path)
        except SectionNotFoundError as e:
            # Check if section exists in content but not TOC
            from ..section_parser import parse_sections, find_section

            try:
                _, sections = parse_sections(body)
                find_section(sections, section_path)
                # Section exists in content but not TOC - this is a sync error
                raise TOCSyncError(
                    f"Section {section_path} exists in content but not in TOC metadata. Run sync_header first."
                ) from e
            except SectionNotFoundError:
                # Section doesn't exist anywhere
                raise SectionNotFoundError(
                    f"Section {section_path} not found in {filename}"
                ) from e

        check_abstract_length(abstract, level, config)

        old_abstract = section.abstract
        # Update TOC with new abstract
        fm.toc = update_toc_abstract(fm.toc, section_path, abstract)

        action = f"updated abstract for section '{section_path}' in {filename}"
        if old_abstract.strip() == abstract.strip():
            return f"ACTION: no change needed for section '{section_path}' in {filename} (abstract already identical)\nNEXT_STEPS:\n  - abstract is up to date"

    # Write updated file
    write_file(docs_dir, filename, fm, body)

    # Generate intelligent NEXT_STEPS
    next_steps = []

    # Suggest related abstract updates if this was a significant change
    if len(abstract.strip()) > len(old_abstract.strip()) * 1.5:
        next_steps.append(
            f"consider updating abstracts for related sections in {filename}"
        )

    # Suggest file-level abstract update if section was significantly changed
    if (
        section_path is not None
        and len(abstract.strip()) > len(old_abstract.strip()) * 2
    ):
        next_steps.append(
            f"review file-level abstract for {filename} (may need updating)"
        )

    # Suggest review of references if abstract meaningfully changed
    if len(abstract.strip()) > 20 and old_abstract.strip() != abstract.strip():
        next_steps.append(
            "run get_pending_actions to check for any reference updates needed"
        )

    if not next_steps:
        next_steps.append("abstract update completed successfully")

    next_steps_str = "\n  ".join(["  - " + step for step in next_steps])

    return f"ACTION: {action}\nNEXT_STEPS:\n{next_steps_str}"
