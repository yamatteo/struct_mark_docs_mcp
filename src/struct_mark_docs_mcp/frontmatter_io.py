from pathlib import Path

import frontmatter
import yaml

from .exceptions import DocsFileNotFoundError
from .models import FileFrontmatter


def resolve_path(docs_dir: Path, filename: str) -> Path:
    """Resolve filename relative to docs_dir, raising if outside the directory."""
    path = (docs_dir / filename).resolve()
    if not path.is_relative_to(docs_dir.resolve()):
        raise DocsFileNotFoundError(f"{filename!r} is outside the docs directory")
    return path


def read_file(docs_dir: Path, filename: str) -> tuple[FileFrontmatter, str]:
    """Read a markdown file and return its frontmatter model and body text."""
    path = resolve_path(docs_dir, filename)
    if not path.exists():
        raise DocsFileNotFoundError(f"{filename!r} not found in docs directory")
    post = frontmatter.load(str(path))
    metadata = dict(post.metadata)
    if "title" not in metadata:
        metadata["title"] = path.stem
    return FileFrontmatter.model_validate(metadata), post.content


def write_file(docs_dir: Path, filename: str, fm: FileFrontmatter, body: str) -> None:
    """Write a markdown file with canonical YAML frontmatter key order."""
    path = resolve_path(docs_dir, filename)
    yaml_str = yaml.dump(
        fm.to_ordered_dict(),
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    path.write_text(f"---\n{yaml_str}---\n\n{body.lstrip(chr(10))}", encoding="utf-8")
