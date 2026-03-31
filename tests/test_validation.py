import pytest

from struct_mark_docs_mcp.config import DocsConfig
from struct_mark_docs_mcp.exceptions import (
    DuplicateSectionError,
    InjectionError,
    ValidationError,
)
from struct_mark_docs_mcp.validation import (
    check_abstract_length,
    check_no_heading_injection,
    check_unique_section_title,
    to_snake,
    validate_snake_filename,
)


# ---------------------------------------------------------------------------
# to_snake
# ---------------------------------------------------------------------------


def test_to_snake_alphanumeric_passthrough():
    assert to_snake("hello_world") == "hello_world"
    assert to_snake("abc123") == "abc123"


def test_to_snake_special_chars_become_underscores():
    assert to_snake("Hello World!") == "hello_world"
    assert to_snake("Foo-Bar") == "foo_bar"
    assert to_snake("a  b") == "a_b"


def test_to_snake_strips_leading_trailing_underscores():
    assert to_snake("_hello_") == "hello"
    assert to_snake("---hi---") == "hi"


def test_to_snake_255_char_limit():
    long = "a" * 300
    result = to_snake(long)
    assert len(result) == 255


# ---------------------------------------------------------------------------
# validate_snake_filename
# ---------------------------------------------------------------------------


def test_validate_snake_filename_valid():
    validate_snake_filename("my_file.md")
    validate_snake_filename("readme.md")
    validate_snake_filename("a1b2.md")


def test_validate_snake_filename_rejects_camel_case():
    with pytest.raises(ValidationError):
        validate_snake_filename("MyFile.md")


def test_validate_snake_filename_rejects_spaces():
    with pytest.raises(ValidationError):
        validate_snake_filename("my file.md")


def test_validate_snake_filename_rejects_empty_stem():
    with pytest.raises(ValidationError):
        validate_snake_filename(".md")


# ---------------------------------------------------------------------------
# check_abstract_length
# ---------------------------------------------------------------------------


def test_check_abstract_length_exact_limit_passes():
    cfg = DocsConfig()
    check_abstract_length("x" * cfg.abstract_limit_file, level=0, config=cfg)
    check_abstract_length("x" * cfg.abstract_limit_section, level=1, config=cfg)
    check_abstract_length("x" * cfg.abstract_limit_subsection, level=2, config=cfg)
    check_abstract_length("x" * cfg.abstract_limit_subsubsection, level=3, config=cfg)


def test_check_abstract_length_over_limit_raises():
    cfg = DocsConfig()
    with pytest.raises(ValidationError):
        check_abstract_length("x" * (cfg.abstract_limit_file + 1), level=0, config=cfg)
    with pytest.raises(ValidationError):
        check_abstract_length("x" * (cfg.abstract_limit_section + 1), level=1, config=cfg)
    with pytest.raises(ValidationError):
        check_abstract_length("x" * (cfg.abstract_limit_subsection + 1), level=2, config=cfg)
    with pytest.raises(ValidationError):
        check_abstract_length("x" * (cfg.abstract_limit_subsubsection + 1), level=3, config=cfg)


def test_check_abstract_length_empty_passes():
    check_abstract_length("", level=0, config=DocsConfig())


# ---------------------------------------------------------------------------
# check_no_heading_injection
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("hashes", ["#", "##", "###", "####", "#####", "######"])
def test_check_no_heading_injection_atx_raises(hashes):
    with pytest.raises(InjectionError):
        check_no_heading_injection(f"{hashes} Heading\n\nSome text.")


def test_check_no_heading_injection_setext_equals_raises():
    with pytest.raises(InjectionError):
        check_no_heading_injection("Heading\n======\n\nText.")


def test_check_no_heading_injection_setext_dashes_raises():
    with pytest.raises(InjectionError):
        check_no_heading_injection("Heading\n------\n\nText.")


def test_check_no_heading_injection_normal_prose_passes():
    check_no_heading_injection("Just some normal text.\n\nNo headings here.")


def test_check_no_heading_injection_hashtag_no_space_passes():
    check_no_heading_injection("Use #hashtag in social media.\n\n#noheading")


def test_check_no_heading_injection_atx_inline_passes():
    # ATX heading pattern requires start-of-line; inline # is fine
    check_no_heading_injection("Color #ff0000 is red.")


# ---------------------------------------------------------------------------
# check_unique_section_title
# ---------------------------------------------------------------------------


def test_check_unique_section_title_exact_match_raises():
    with pytest.raises(DuplicateSectionError):
        check_unique_section_title("Introduction", ["Introduction", "Summary"])


def test_check_unique_section_title_snake_equivalent_raises():
    with pytest.raises(DuplicateSectionError):
        check_unique_section_title("My Section", ["my_section"])


def test_check_unique_section_title_different_passes():
    check_unique_section_title("Conclusion", ["Introduction", "Summary"])


def test_check_unique_section_title_empty_list_passes():
    check_unique_section_title("New Section", [])
