import re
from pathlib import Path

from .config import DocsConfig
from .exceptions import DuplicateSectionError, InjectionError, ValidationError

_ATX_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
_SETEXT_RE = re.compile(r"^[=-]{2,}\s*$", re.MULTILINE)


def to_snake(title: str) -> str:
    """Normalise a title to snake_case for path matching."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", title).lower().strip("_")[:255]


def validate_snake_filename(filename: str) -> None:
    """Raise ValidationError if filename stem is not valid snake_case."""
    stem = Path(filename).stem
    if not stem or to_snake(stem) != stem:
        raise ValidationError(
            f"Filename stem {stem!r} is not valid snake_case"
        )


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
