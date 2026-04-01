import re
from pathlib import Path

import yaml

from ..config import DocsConfig
from ..frontmatter_io import read_file, write_file
from ..models import SectionMeta, SubsectionMeta, SubsubsectionMeta
from ..section_parser import parse_sections
from ..validation import to_snake
from .refs_ops import update_back_refs

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


def read_header(docs_dir: Path, filename: str) -> str:
    """Return the YAML frontmatter of a file as a formatted string."""
    fm, _ = read_file(docs_dir, filename)
    return yaml.dump(
        fm.to_ordered_dict(),
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


def _build_toc(sections: list, old_by_snake: dict) -> list[SectionMeta]:
    result = []
    for sec in sections:
        key = to_snake(sec.title)
        old_sec = old_by_snake.get(key)
        old_subs = {to_snake(s.title): s for s in old_sec.subsections} if old_sec else {}

        new_subs = []
        for sub in sec.children:
            sub_key = to_snake(sub.title)
            old_sub = old_subs.get(sub_key)
            old_subsubs = {to_snake(s.title): s for s in old_sub.subsubsections} if old_sub else {}

            new_subsubs = []
            for subsub in sub.children:
                subsub_key = to_snake(subsub.title)
                old_subsub = old_subsubs.get(subsub_key)
                new_subsubs.append(SubsubsectionMeta(
                    title=subsub.title,
                    abstract=old_subsub.abstract if old_subsub else "",
                    wc=len(subsub.body.split()),
                ))

            new_subs.append(SubsectionMeta(
                title=sub.title,
                abstract=old_sub.abstract if old_sub else "",
                wc=len(sub.body.split()),
                subsubsections=new_subsubs,
            ))

        result.append(SectionMeta(
            title=sec.title,
            abstract=old_sec.abstract if old_sec else "",
            wc=len(sec.body.split()),
            subsections=new_subs,
        ))
    return result


def sync_header(docs_dir: Path, config: DocsConfig, filename: str) -> str:
    """Recompute wc, rebuild toc (preserving abstracts), scan refs, write file."""
    fm, body = read_file(docs_dir, filename)
    _, sections = parse_sections(body)

    fm.wc = len(body.split())
    old_by_snake = {to_snake(s.title): s for s in fm.toc}
    fm.toc = _build_toc(sections, old_by_snake)
    old_refs = fm.refs
    fm.refs = scan_refs(body)

    write_file(docs_dir, filename, fm, body)
    update_back_refs(docs_dir, filename, old_refs, fm.refs)

    return (
        f"ACTION: synced header for {filename}\n"
        "NEXT_STEPS:\n"
        "  - update abstracts for any sections missing them\n"
        "  - run get_pending_actions to see remaining tasks"
    )
