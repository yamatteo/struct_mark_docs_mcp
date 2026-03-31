# struct-mark-docs-mcp — Project Guide

## Development Rules
- This is a `uv`-managed Python package. Every Python invocation goes through `uv run`.
- After each development iteration: `uv run pytest` (tests must pass) and `uv run ruff check` (no lint errors).
- Each iteration must be small and committed with git before moving to the next.
- No features beyond what the current todo item requires.

## Project Overview
An MCP server for managing structured markdown documentation. It:
- Operates only on `.md` files in `MARKDOWN_DOCS_DIR` (env var, defaults to `.`)
- Manages YAML frontmatter: title, abstract, wc, toc, refs, back_refs
- Provides structure-aware section CRUD tools
- Returns NEXT_STEPS instructions to the calling agent after each modifying operation
- Manages references and back-references across files automatically

## Configuration File
Docs directory may contain `.struct-mark.yaml` with:
```yaml
description: "..."
index_file: README.md
abstract_limit_file: 380
abstract_limit_section: 288
abstract_limit_subsection: 204
abstract_limit_subsubsection: 128
section_wc_soft_limit: 800
```
Missing file → use defaults.

## Frontmatter Schema
```yaml
title: snake_case_filename
abstract: |
  File-level abstract (max 380 chars).
wc: 240
toc:
  - title: Section Title
    abstract: |
      Section abstract (max 288 chars).
    wc: 150
    subsections:
      - title: Subsection Title
        abstract: |
          Subsection abstract (max 204 chars).
        wc: 70
        subsubsections:
          - title: Subsubsection Title
            abstract: |
              Subsubsection abstract (max 128 chars).
            wc: 20
refs:
  - other_file_snake_title
back_refs:
  - parent_file_snake_title
```

## Module Structure
```
src/struct_mark_docs_mcp/
    __init__.py           # main() entry point
    server.py             # FastMCP instance, lifespan, all tool registrations
    config.py             # DocsConfig (Pydantic) + load_config()
    models.py             # FileFrontmatter, SectionMeta, SubsectionMeta, SubsubsectionMeta
    frontmatter_io.py     # read_file(), write_file(), resolve_path()
    section_parser.py     # parse_sections(), render_sections(), find_section()
    validation.py         # to_snake(), check_abstract_length(), check_no_heading_injection(), etc.
    exceptions.py         # DocsMCPError hierarchy
    ops/
        __init__.py
        list_ops.py
        header_ops.py
        abstract_ops.py
        section_ops.py
        refs_ops.py
        pending_ops.py
tests/
    conftest.py
    test_config.py
    test_validation.py
    test_frontmatter_io.py
    test_section_parser.py
    test_ops/
        test_list_ops.py
        test_header_ops.py
        test_abstract_ops.py
        test_section_ops.py
        test_refs_ops.py
        test_pending_ops.py
```

## MCP Tools
| Tool | Description |
|------|-------------|
| `list_files` | List all .md files with status (wc, abstract status) |
| `read_header` | Read YAML frontmatter of a file |
| `sync_header` | Recompute wc, toc structure, refs from file content; update back_refs in referenced files |
| `update_abstract` | Update abstract for file or a section path; validates char limits |
| `read_section` | Read content of a section by path (e.g. `"Introduction/Overview"`) |
| `write_section` | Replace section body; prevents heading injection; updates wc; returns NEXT_STEPS |
| `add_section` | Add section/subsection/subsubsection at a position |
| `remove_section` | Remove section and children |
| `rename_section` | Rename section; flags files needing ref updates |
| `get_pending_actions` | Emit prioritised action list (missing abstracts, over-limit, broken refs) |

## Post-modification Response Format
All modifying tools return:
```
ACTION: <what was done>
NEXT_STEPS:
  - update abstract for section "X" in file.md
  - update abstract for file.md (parent level)
  - consider reviewing references in: a.md, b.md
```

## Key Invariants
- Path traversal: all file access goes through `resolve_path()` which checks `.is_relative_to(docs_dir)`
- Heading injection: `write_section` rejects content containing `^#{1,6}\s` or setext underlines
- Abstract limits: refused hard (raise ToolError), not just warned
- Snake titles: `re.sub(r'[^a-zA-Z0-9]+', '_', title).lower().strip('_')[:255]`
- Section paths: slash-separated display titles, matched via snake equivalence
- Only levels 1-3 (`#`, `##`, `###`) are managed; deeper levels are body text

---

## Todo List

### Phase 0 — Project Scaffolding
- [x] Write CLAUDE.md
- [x] Add dependencies to `pyproject.toml`: `mcp>=1.6.0`, `python-frontmatter>=1.1.0`, `pyyaml>=6.0.2`, `pydantic>=2.0`; dev deps: `pytest>=8.0`, `pytest-anyio`, `ruff>=0.4`
- [x] Create `exceptions.py`: `DocsMCPError`, `ConfigError`, `FileNotFoundError`, `ValidationError`, `InjectionError`, `SectionNotFoundError`, `DuplicateSectionError`
- [x] Create `config.py`: `DocsConfig` Pydantic model + `load_config(docs_dir)` (tries `.struct-mark.yaml` then `struct-mark.yaml`, defaults on missing, raises ConfigError on parse error)
- [x] Create `models.py`: `SubsubsectionMeta`, `SubsectionMeta`, `SectionMeta`, `FileFrontmatter` (Pydantic)
- [x] Create minimal `server.py`: `AppState` dataclass, `lifespan` reading `MARKDOWN_DOCS_DIR`, `create_server() -> FastMCP`
- [x] Update `__init__.py`: `main()` calls `create_server().run(transport="stdio")`
- [x] Commit: `feat: bootstrap FastMCP server skeleton`

### Phase 1 — Core Parsing Infrastructure
- [x] Create `frontmatter_io.py`: `read_file()`, `write_file()` (canonical key order, no sort_keys), `resolve_path()` (path traversal guard)
- [x] Create `section_parser.py`: `SectionBlock` dataclass, `parse_sections()` (regex ATX headings levels 1-3), `render_sections()`, `find_section(path)` (snake equivalence), `section_path_to_key()`
- [x] Add `tests/test_frontmatter_io.py` and `tests/test_section_parser.py`
- [x] Run `uv run pytest` and `uv run ruff check`
- [x] Commit: `feat: frontmatter I/O and section parser`

### Phase 2 — Validation
- [x] Create `validation.py`: `to_snake()`, `validate_snake_filename()`, `check_abstract_length(abstract, level, config)`, `check_no_heading_injection()` (ATX + setext), `check_unique_section_title()`
- [x] Add `tests/test_validation.py` (boundary values, injection patterns)
- [x] Run `uv run pytest` and `uv run ruff check`
- [x] Commit: `feat: validation utilities`

### Phase 3 — ops/list_ops and ops/header_ops
- [x] Create `ops/list_ops.py`: `list_files(docs_dir)` → one line per file with wc and abstract status
- [x] Create `ops/header_ops.py`: `read_header()`, `sync_header()` (recompute wc, rebuild toc preserving existing abstracts, scan refs links, call `update_back_refs`)
- [x] Register `list_files` and `read_header` and `sync_header` tools in `server.py`
- [x] Add tests
- [x] Run `uv run pytest` and `uv run ruff check`
- [x] Commit: `feat: list_files, read_header, sync_header tools`

### Phase 4 — ops/abstract_ops
- [ ] Create `ops/abstract_ops.py`: `update_abstract(docs_dir, config, filename, abstract, section_path=None)` (traverse toc model by snake-path, validate length, write)
- [ ] Register `update_abstract` tool in `server.py`
- [ ] Add tests (file-level, section-level, overlimit rejection)
- [ ] Run `uv run pytest` and `uv run ruff check`
- [ ] Commit: `feat: update_abstract tool`

### Phase 5 — ops/section_ops
- [ ] Create `ops/section_ops.py`:
  - `read_section(docs_dir, filename, section_path)` — returns heading + body-only slice + children
  - `write_section(docs_dir, config, filename, section_path, content)` — injection check, replace body-only, recompute wc, return NEXT_STEPS
  - `add_section(docs_dir, config, filename, title, level, parent_path, position)` — uniqueness check, insert, sync toc
  - `remove_section(docs_dir, filename, section_path)`
  - `rename_section(docs_dir, config, filename, section_path, new_title)` — update heading + toc, flag affected files
- [ ] Register all 5 tools in `server.py`
- [ ] Add `tests/test_ops/test_section_ops.py`
- [ ] Run `uv run pytest` and `uv run ruff check`
- [ ] Commit: `feat: section CRUD tools`

### Phase 6 — ops/refs_ops
- [ ] Create `ops/refs_ops.py`: `update_back_refs(docs_dir, referencing_file, old_refs, new_refs)` — diff added/removed, update target files' back_refs; `scan_refs(body)` — regex link detection
- [ ] Wire into `sync_header` and `write_section`
- [ ] Add `tests/test_ops/test_refs_ops.py`
- [ ] Run `uv run pytest` and `uv run ruff check`
- [ ] Commit: `feat: reference and back-reference management`

### Phase 7 — ops/pending_ops
- [ ] Create `ops/pending_ops.py`: `get_pending_actions(docs_dir, config)` — scan all files for empty abstracts, over-limit abstracts, over-limit sections, broken refs, inconsistent back_refs
- [ ] Register `get_pending_actions` tool in `server.py`
- [ ] Add `tests/test_ops/test_pending_ops.py`
- [ ] Run `uv run pytest` and `uv run ruff check`
- [ ] Commit: `feat: get_pending_actions tool`

### Phase 8 — Integration Hardening
- [ ] Add `initialise_file()` helper: auto-populate frontmatter for bare `.md` files on first access
- [ ] Standardise all modifying tool responses to the `ACTION: ... NEXT_STEPS: ...` format
- [ ] Add server-level integration tests in `tests/test_server.py`
- [ ] Run full test suite
- [ ] Commit: `feat: integration hardening and consistent response format`

### Phase 9 — Documentation
- [ ] Write `README.md`: installation (`uv add struct-mark-docs-mcp` / `uvx`), quickstart (set `MARKDOWN_DOCS_DIR`, wire into Claude Desktop / MCP client), all config keys with types and defaults, full MCP tool reference (inputs, outputs, example calls), post-modification response format, key invariants (path traversal guard, heading injection, abstract limits)
- [ ] Commit: `docs: write README with installation, configuration and tool reference`
