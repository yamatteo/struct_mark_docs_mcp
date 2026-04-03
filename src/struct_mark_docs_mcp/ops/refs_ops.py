import re
from pathlib import Path

from ..frontmatter_io import read_file, write_file
from ..validation import to_snake

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+\.md[^)]*)\)")


def scan_refs(body: str) -> list[str]:
    """Extract snake_case stems from .md links in body, deduplicated, order-preserving."""
    refs: list[str] = []
    seen: set[str] = set()
    for m in _LINK_RE.finditer(body):
        href = m.group(1).split("#")[0].strip()
        if href.endswith(".md"):
            key = to_snake(Path(href).stem)
            if key not in seen:
                seen.add(key)
                refs.append(key)
    return refs


def update_back_refs(
    docs_dir: Path,
    referencing_file: str,
    old_refs: list[str],
    new_refs: list[str],
) -> None:
    """Diff old vs new refs; add/remove referencing_file's key from target files' back_refs."""
    referencing_key = to_snake(Path(referencing_file).stem)
    added = set(new_refs) - set(old_refs)
    removed = set(old_refs) - set(new_refs)

    key_to_name = {to_snake(f.stem): f.name for f in docs_dir.glob("*.md")}

    for ref_key in added:
        target_name = key_to_name.get(ref_key)
        if target_name is None or target_name == referencing_file:
            continue
        fm, body = read_file(docs_dir, target_name)
        if referencing_key not in fm.back_refs:
            fm.back_refs = sorted(set(fm.back_refs) | {referencing_key})
            write_file(docs_dir, target_name, fm, body)

    for ref_key in removed:
        target_name = key_to_name.get(ref_key)
        if target_name is None or target_name == referencing_file:
            continue
        fm, body = read_file(docs_dir, target_name)
        if referencing_key in fm.back_refs:
            fm.back_refs = [r for r in fm.back_refs if r != referencing_key]
            write_file(docs_dir, target_name, fm, body)
