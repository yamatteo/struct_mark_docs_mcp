# Issues

This file lists all identified gaps, bugs, and improvements found by comparing the implementation against `ORIGINAL_PROMPT.md`, `CLAUDE.md`, and the `README.md`.

Each task is self-contained and can be executed independently unless a dependency is noted.

---

## ISSUE-01 — Level calculation in `update_abstract` is broken for paths with leading/trailing slashes

**File**: `src/struct_mark_docs_mcp/ops/abstract_ops.py:52`

**Problem**: The abstract validation level is computed as:
```python
level = len(section_path.split("/"))
```
This does **not** filter empty strings produced by leading or trailing slashes.  
For example `"/Introduction/"` produces `len(["", "Introduction", ""]) = 3` (subsubsection limit),  
but the path has only one real component so the correct level is 1 (section limit).  
The path filtering at line 81 **does** filter empties correctly, making the two computations inconsistent.

**Fix**: Replace the level calculation with:
```python
path_parts = [p.strip() for p in section_path.split("/") if p.strip()]
level = len(path_parts)
```
and then reuse `path_parts` at line 81 instead of splitting again.

**Tests to add**: `tests/test_ops/test_abstract_ops.py` — test `update_abstract` with paths like `"/Introduction/"`, `"Introduction/"`, `"/Introduction"`.

---

## ISSUE-02 — `update_toc_recursive` silently skips update when subsection list in TOC is empty

**File**: `src/struct_mark_docs_mcp/ops/abstract_ops.py:70-77`

**Problem**: The traversal condition is:
```python
if hasattr(item, "subsections") and item.subsections:     # falsy when list is []
    ...
elif hasattr(item, "subsubsections") and item.subsubsections:  # falsy when list is []
    ...
return toc_list   # silently returns without updating anything
```
If `sync_header` has not been called after adding a subsection (so it exists in the body but the TOC model still has `subsections=[]`), calling `update_abstract` on that subsection will silently succeed (return `ACTION: ...`) while the abstract is never written.

**Fix**: Always attempt deeper traversal regardless of whether the child list is empty. Change the conditions to check only `hasattr` (not truthiness):
```python
if hasattr(item, "subsections"):
    item.subsections = update_toc_recursive(item.subsections, path_parts[1:])
elif hasattr(item, "subsubsections"):
    item.subsubsections = update_toc_recursive(item.subsubsections, path_parts[1:])
```
If the child list is empty the recursive call will find nothing and the operation will naturally fall through without updating — this is the correct behavior.

**Tests to add**: `tests/test_ops/test_abstract_ops.py` — test updating a subsection abstract when the parent section has an empty `subsections` list in its TOC model (out-of-sync scenario).

---

## ISSUE-03 — `update_back_refs` is called twice in `write_section`, `remove_section`, and `rename_section`

**Files**: `src/struct_mark_docs_mcp/ops/section_ops.py:50,54` / `164,168` / `214,218`

**Problem**: Each of those three functions first calls `update_back_refs(old_refs, new_refs)` directly, then immediately calls `sync_header()`. `sync_header` also calls `update_back_refs(old_refs_from_disk, new_refs_from_scan)` — effectively with the same arguments. The second call is a no-op due to idempotency guards, but it triggers unnecessary file I/O (reading and writing every referenced file a second time).

**Fix**: Remove the explicit `update_back_refs` call from `write_section`, `remove_section`, and `rename_section` and let `sync_header` do it as part of its normal flow. The three functions should simply call `sync_header` after writing; they should not call `update_back_refs` themselves.

**Note**: Verify no test relies on the order (back_refs update before or after sync). After the fix `sync_header` remains the single source of truth for ref/back_ref consistency.

---

## ISSUE-04 — README example passes a heading into `write_section` content (would throw InjectionError)

**File**: `README.md:262-264`

**Problem**: The "Example Workflow" section shows:
```
write_section(filename="guide.md", section_path="Getting Started", content="# Getting Started

This is the getting started section...")
```
The `content` string starts with `# Getting Started`, which is an ATX heading. `write_section` calls `check_no_heading_injection` and would raise an `InjectionError` on this input. The example is misleading and wrong.

**Fix**: Remove the heading line from the example content so it reads:
```
write_section(filename="guide.md", section_path="Getting Started",
              content="This is the getting started section with detailed instructions...")
```

---

## ISSUE-05 — README installation shows `uv install` (invalid command)

**File**: `README.md:31`

**Problem**: The "Manual installation" block shows `uv install`, which is not a valid `uv` command. The correct command is `uv sync`.

**Fix**: Replace `uv install` with `uv sync`.

---

## ISSUE-06 — README has placeholder text in License and Contributing sections

**File**: `README.md:291-295`

**Problem**: Both the License and Contributing sections contain `[Add your license information here]` and `[Add contribution guidelines here]` placeholder text. A published README should not have unfilled placeholders.

**Fix**: Choose and state a license (the project currently has no `LICENSE` file either). A minimal acceptable fix is to add `MIT` or `Apache 2.0` and create a `LICENSE` file, or to remove those sections entirely until the author decides.

---

## ISSUE-07 — `update_abstract` returns a trivial NEXT_STEPS that violates the spec

**File**: `src/struct_mark_docs_mcp/ops/abstract_ops.py:89`

**Problem**: The response is:
```
ACTION: updated abstract for section 'X' in file.md
NEXT_STEPS:
  - abstract update completed successfully
```
The spec (`CLAUDE.md` — "Post-modification Response Format") says modifying tools should include meaningful next steps such as suggesting the parent abstract be checked and pointing to `get_pending_actions`. The current message provides no actionable guidance.

**Fix**: Replace the NEXT_STEPS with context-aware suggestions:
- For a file-level abstract update: suggest running `get_pending_actions`.
- For a section-level update: suggest updating the parent-section abstract (or file abstract if it's a top-level section), then running `get_pending_actions`.

Example:
```python
if section_path is None:
    next_steps = "  - run get_pending_actions to check for remaining tasks"
else:
    parts = [p.strip() for p in section_path.split("/") if p.strip()]
    parent = "/".join(parts[:-1])
    parent_note = (
        f"  - update abstract for '{parent}' in {filename}\n" if parent
        else f"  - update file-level abstract for {filename}\n"
    )
    next_steps = parent_note + "  - run get_pending_actions to check for remaining tasks"
```

---

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
