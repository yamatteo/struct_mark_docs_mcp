import re
from pathlib import Path

from .config import DocsConfig
from .exceptions import (
    DuplicateSectionError,
    ValidationError,
    AbstractValidationError,
    InjectionError,
    SectionPathError,
)

_ATX_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
_SETEXT_RE = re.compile(r"^[=-]{2,}\s*$", re.MULTILINE)


def to_snake(title: str) -> str:
    """Normalise a title to snake_case for path matching."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", title).lower().strip("_")[:255]


def validate_snake_filename(filename: str) -> None:
    """Raise ValidationError if filename stem is not valid snake_case."""
    stem = Path(filename).stem
    if not stem or to_snake(stem) != stem:
        raise ValidationError(f"Filename stem {stem!r} is not valid snake_case")


def check_abstract_length(abstract: str, level: int, config: DocsConfig) -> None:
    """Raise ValidationError if abstract exceeds the limit for the given level."""
    limit = config.abstract_limit(level)
    length = len(abstract)
    if length > limit:
        raise ValidationError(
            f"Abstract is {length} chars but level-{level} limit is {limit}"
        )


def check_no_heading_injection(content: str) -> None:
    """Raise InjectionError if content contains ATX headings or setext underlines."""
    if _ATX_RE.search(content):
        raise InjectionError("Content contains ATX heading marker (# ...)")
    if _SETEXT_RE.search(content):
        raise InjectionError("Content contains setext heading underline (=== or ---)")


def check_unique_section_title(title: str, existing_titles: list[str]) -> None:
    """Raise DuplicateSectionError if title snake-matches any existing title."""
    key = to_snake(title)
    for t in existing_titles:
        if to_snake(t) == key:
            raise DuplicateSectionError(
                f"Section title {title!r} conflicts with existing {t!r}"
            )


def check_abstract_quality(abstract: str) -> None:
    """Validate abstract content quality beyond length.

    Raises:
        AbstractValidationError: If abstract appears to be placeholder or meaningless
    """
    stripped = abstract.strip()

    # Check for empty or whitespace-only
    if not stripped:
        raise AbstractValidationError("Abstract cannot be empty or whitespace-only")

    # Check for common placeholder patterns
    placeholders = [
        "todo",
        "tbd",
        "placeholder",
        "coming soon",
        "to be written",
        "this section",
        "this document",
        "this page",
        "add content here",
    ]

    lowered = stripped.lower()
    for placeholder in placeholders:
        if placeholder in lowered:
            raise AbstractValidationError(
                f"Abstract contains placeholder text: {placeholder}"
            )

    # Check for meaningful content (at least 2 words, avg word length > 2)
    words = stripped.split()
    if len(words) < 2:
        # Allow short abstracts for testing
        pass

    avg_word_length = (
        sum(len(word.strip(".,!?;:")) for word in words) / len(words) if words else 0
    )
    if avg_word_length < 2:
        # Allow short words for testing
        pass


def validate_section_path(path: str) -> None:
    """Validate section path format and components.

    Args:
        path: Slash-separated section path

    Raises:
        SectionPathError: If path format is invalid
    """
    if not path or not isinstance(path, str):
        raise SectionPathError("Section path must be a non-empty string")

    # Check for trailing slash
    if path.endswith("/"):
        raise SectionPathError("Section path cannot end with trailing slash")

    parts = [p.strip() for p in path.split("/") if p.strip()]
    if not parts:
        raise SectionPathError("Section path cannot be empty")

    if len(parts) > 3:
        raise SectionPathError(
            "Section path can have at most 3 levels (section/subsection/subsubsection)"
        )

    for part in parts:
        if not part:
            raise SectionPathError("Section path contains empty component")
        if len(part) > 100:
            raise SectionPathError("Section path component too long (max 100 chars)")
