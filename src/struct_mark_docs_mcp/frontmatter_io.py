from pathlib import Path

import frontmatter
import yaml

from .exceptions import DocsFileNotFoundError
from .models import FileFrontmatter
from .validation import validate_snake_filename


def resolve_path(docs_dir: Path, filename: str) -> Path:
    """Resolve filename relative to docs_dir, raising if outside the directory."""
    validate_snake_filename(filename)
    path = (docs_dir / filename).resolve()
    if not path.is_relative_to(docs_dir.resolve()):
        raise DocsFileNotFoundError(f"{filename!r} is outside the docs directory")
    return path


def initialise_file(docs_dir: Path, filename: str) -> FileFrontmatter:
    """Write minimal frontmatter to a bare .md file and return it."""
    from .validation import to_snake  # local import avoids circular dependency
    path = resolve_path(docs_dir, filename)
    post = frontmatter.load(str(path))
    fm = FileFrontmatter(title=to_snake(path.stem))
    write_file(docs_dir, filename, fm, post.content)
    return fm


def read_file(docs_dir: Path, filename: str) -> tuple[FileFrontmatter, str]:
    """Read a markdown file and return its frontmatter model and body text."""
    path = resolve_path(docs_dir, filename)
    if not path.exists():
        raise DocsFileNotFoundError(f"{filename!r} not found in docs directory")
    post = frontmatter.load(str(path))
    # python-frontmatter strips trailing newlines; restore one so section
    # parsers always see a trailing \n and sections don't lose their separator.
    content = post.content
    if content and not content.endswith("\n"):
        content += "\n"
    if not post.metadata:  # bare file — auto-initialise
        return initialise_file(docs_dir, filename), content
    metadata = dict(post.metadata)
    if "title" not in metadata:
        metadata["title"] = path.stem
    return FileFrontmatter.model_validate(metadata), content


def write_file(docs_dir: Path, filename: str, fm: FileFrontmatter, body: str) -> None:
    """Write a markdown file with canonical YAML frontmatter key order."""
    path = resolve_path(docs_dir, filename)
    yaml_str = yaml.dump(
        fm.to_ordered_dict(),
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    path.write_text(f"---\n{yaml_str}---\n\n{body.lstrip("\n")}", encoding="utf-8")
