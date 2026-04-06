from pathlib import Path

from ..config import DocsConfig
from ..frontmatter_io import read_file


def _abstract_status(abstract: str, limit: int) -> str:
    if not abstract.strip():
        return "missing"
    n = len(abstract)
    if n > limit:
        return f"overlimit({n}/{limit})"
    return f"ok({n}/{limit})"


def list_files(docs_dir: Path, config: DocsConfig) -> str:
    """Return one line per .md file with wc and abstract status."""
    files = sorted(docs_dir.rglob("*.md"))
    if not files:
        return "(no markdown files found)"
    lines = []
    for f in files:
        relative_path = f.relative_to(docs_dir)
        fm, _ = read_file(docs_dir, str(relative_path))
        status = _abstract_status(fm.abstract, config.abstract_limit_file)
        lines.append(f"{relative_path}  wc={fm.wc}  abstract={status}")
    return "\n".join(lines)
