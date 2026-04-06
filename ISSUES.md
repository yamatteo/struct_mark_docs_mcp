# Issues

This file lists all identified gaps, bugs, and improvements found by comparing the implementation against `ORIGINAL_PROMPT.md`, `CLAUDE.md`, and the `README.md`.

Each task is self-contained and can be executed independently unless a dependency is noted.

## ISSUE-08 — Subdirectory scanning not implemented (ORIGINAL_PROMPT requirement)

**Files**: `src/struct_mark_docs_mcp/ops/list_ops.py:18`, `ops/pending_ops.py:19`, `ops/refs_ops.py:35`

**Problem**: `ORIGINAL_PROMPT.md` states: "the server will be started from the docs root and will be able to access, read and modify only markdown file in that directory **or its subdirectories**." All three ops files use `docs_dir.glob("*.md")`, which only matches files in the root and ignores subdirectories.

**Fix**: Replace `docs_dir.glob("*.md")` with `docs_dir.rglob("*.md")` in all three files. Verify path-related operations (e.g. ref key generation from `f.stem`) still work correctly when files are in subdirectories (the stem approach is fine; it may however produce key collisions if two files in different subdirectories share the same stem — that edge case should be documented).

**Note**: All read/write operations in `frontmatter_io.py` already use `resolve_path()` which supports subdirectory paths. Only the discovery/listing functions need updating. After the change, update `list_files` to show relative paths (e.g. `subdir/file.md`) rather than bare filenames so the caller can distinguish files in different subdirectories.

---

## ISSUE-09 — `validate_snake_filename` is never called when files are accessed

**File**: `src/struct_mark_docs_mcp/validation.py:19-25`, `frontmatter_io.py`

**Problem**: `validate_snake_filename` exists and is exported, but it is not called anywhere in the codebase — neither in `read_file`, `write_file`, nor in any tool handler. Per `ORIGINAL_PROMPT.md`: "titles that can't be file name will be escaped … duplicate titles will be refused". Currently any filename (including ones that would fail the snake_case check) is accepted silently.

**Fix**: Call `validate_snake_filename(filename)` inside `resolve_path()` (or at the top of `read_file` / `write_file`) so invalid filenames are rejected early. Add a test that passes a non-snake filename and expects a `ValidationError`.

---

## ISSUE-10 — `sync_header` word-count counts frontmatter words in some edge cases

**File**: `src/struct_mark_docs_mcp/ops/header_ops.py:80`

**Problem**: The body passed to `sync_header` is obtained via `read_file` which correctly strips frontmatter (`post.content` from `python-frontmatter`). However, `fm.wc = len(body.split())` counts words in the body. Individual section `wc` fields in `_build_toc` are computed from `sec.body.split()` which is the body text between headings — **excluding** child sections. This means the file-level `wc` and section-level `wc` are not comparable: the file `wc` is the total body word count (all sections combined), while section `wc` is only the direct body text (not children). This inconsistency is not documented.

**Fix** (or document): Either:
- Document in code and README that `wc` at the section level counts only the direct body of that section (not nested subsections), while the file-level `wc` counts everything.
- Or change `_build_toc` to compute `wc` as the sum of the direct body plus all nested children — but this would require a recursive count.

A pure documentation fix (adding a comment to `_build_toc` and the README) is acceptable if the current behaviour is intentional.

---

## ISSUE-11 — `initialise_file` does not validate that the filename is snake_case

**File**: `src/struct_mark_docs_mcp/frontmatter_io.py:18-25`

**Problem**: When auto-initialising a bare file, the `title` is set from `to_snake(path.stem)` which normalises the stem. But the actual filename (and therefore the file key used in `refs`/`back_refs`) retains the original, possibly non-snake name. If the file is later referenced by its snake title but stored under a different filename, ref resolution breaks.

**Fix**: In `initialise_file`, after computing `title = to_snake(path.stem)`, warn or raise if `title != path.stem` (i.e., if the filename was not already snake_case). Alternatively, ensure the README notes that managed files **must** have snake_case filenames for refs to work correctly.

---

## ISSUE-12 — `README.md` does not document the automatic bare-file initialisation behaviour

**File**: `README.md`

**Problem**: The `initialise_file` helper (added in Phase 8) automatically adds frontmatter to any `.md` file that is accessed but has no YAML frontmatter. This is a meaningful, non-obvious behaviour that is listed as a feature on line 11 of the README but never explained. A user who reads a bare file will find it has been silently modified, which can be surprising.

**Fix**: Add a short paragraph under "Features" or a new "Bare File Initialization" section explaining that the first access to a bare `.md` file (one without YAML frontmatter) triggers automatic frontmatter creation, and what defaults are used.
