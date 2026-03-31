import pytest

from struct_mark_docs_mcp.config import DocsConfig, load_config
from struct_mark_docs_mcp.exceptions import ConfigError


def test_load_config_defaults(tmp_path):
    config = load_config(tmp_path)
    assert config == DocsConfig()
    assert config.abstract_limit_file == 380
    assert config.abstract_limit(0) == 380
    assert config.abstract_limit(1) == 288
    assert config.abstract_limit(2) == 204
    assert config.abstract_limit(3) == 128


def test_load_config_from_dot_file(tmp_path):
    (tmp_path / ".struct-mark.yaml").write_text(
        "index_file: _index.md\nsection_wc_soft_limit: 500\n"
    )
    config = load_config(tmp_path)
    assert config.index_file == "_index.md"
    assert config.section_wc_soft_limit == 500
    assert config.abstract_limit_file == 380  # default unchanged


def test_load_config_from_plain_file(tmp_path):
    (tmp_path / "struct-mark.yaml").write_text("description: My docs\n")
    config = load_config(tmp_path)
    assert config.description == "My docs"


def test_load_config_dot_file_takes_priority(tmp_path):
    (tmp_path / ".struct-mark.yaml").write_text("description: dot\n")
    (tmp_path / "struct-mark.yaml").write_text("description: plain\n")
    config = load_config(tmp_path)
    assert config.description == "dot"


def test_load_config_malformed_raises(tmp_path):
    (tmp_path / ".struct-mark.yaml").write_text("abstract_limit_file: not_a_number\n")
    with pytest.raises(ConfigError):
        load_config(tmp_path)
