# Issues

This file lists all identified gaps, bugs, and improvements found by comparing the implementation against `ORIGINAL_PROMPT.md`, `CLAUDE.md`, and the `README.md`.

Each task is self-contained and can be executed independently unless a dependency is noted.

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
