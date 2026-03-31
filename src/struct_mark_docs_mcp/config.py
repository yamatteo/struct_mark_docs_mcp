from pathlib import Path

import yaml
from pydantic import BaseModel

from .exceptions import ConfigError


class DocsConfig(BaseModel):
    description: str = ""
    index_file: str = "README.md"
    abstract_limit_file: int = 380
    abstract_limit_section: int = 288
    abstract_limit_subsection: int = 204
    abstract_limit_subsubsection: int = 128
    section_wc_soft_limit: int = 800

    def abstract_limit(self, level: int) -> int:
        """Return abstract char limit for the given nesting level (0=file, 1=section, 2=sub, 3=subsub)."""
        return {
            0: self.abstract_limit_file,
            1: self.abstract_limit_section,
            2: self.abstract_limit_subsection,
            3: self.abstract_limit_subsubsection,
        }.get(level, self.abstract_limit_subsubsection)


def load_config(docs_dir: Path) -> DocsConfig:
    for name in (".struct-mark.yaml", "struct-mark.yaml"):
        path = docs_dir / name
        if path.exists():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                return DocsConfig.model_validate(data)
            except Exception as exc:
                raise ConfigError(f"Failed to parse config file {path}: {exc}") from exc
    return DocsConfig()
