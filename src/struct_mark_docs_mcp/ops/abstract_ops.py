from pathlib import Path

from ..config import DocsConfig
from ..exceptions import SectionNotFoundError
from ..frontmatter_io import read_file, write_file
from ..validation import check_abstract_length, to_snake


def update_abstract(
    docs_dir: Path,
    config: DocsConfig,
    filename: str,
    abstract: str,
    section_path: str | None = None,
) -> str:
    fm, body = read_file(docs_dir, filename)

    if section_path is None:
        check_abstract_length(abstract, 0, config)
        fm.abstract = abstract
        location = filename
    else:
        parts = [p for p in section_path.split("/") if p]
        level = len(parts)  # 1=section, 2=subsection, 3=subsubsection
        check_abstract_length(abstract, level, config)

        snake_parts = [to_snake(p) for p in parts]

        section = next(
            (s for s in fm.toc if to_snake(s.title) == snake_parts[0]), None
        )
        if section is None:
            raise SectionNotFoundError(f"Section {parts[0]!r} not found in {filename}")

        if level == 1:
            section.abstract = abstract
        else:
            subsection = next(
                (s for s in section.subsections if to_snake(s.title) == snake_parts[1]),
                None,
            )
            if subsection is None:
                raise SectionNotFoundError(
                    f"Subsection {parts[1]!r} not found under {parts[0]!r}"
                )

            if level == 2:
                subsection.abstract = abstract
            else:
                subsubsection = next(
                    (
                        s
                        for s in subsection.subsubsections
                        if to_snake(s.title) == snake_parts[2]
                    ),
                    None,
                )
                if subsubsection is None:
                    raise SectionNotFoundError(
                        f"Subsubsection {parts[2]!r} not found under {parts[1]!r}"
                    )
                subsubsection.abstract = abstract

        location = f"section {section_path!r} in {filename}"

    write_file(docs_dir, filename, fm, body)

    return (
        f"ACTION: updated abstract for {location}\n"
        "NEXT_STEPS:\n"
        "  - run get_pending_actions to check for remaining missing abstracts"
    )
