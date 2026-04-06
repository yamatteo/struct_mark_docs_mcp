# Issues

This file lists all identified gaps, bugs, and improvements found by comparing the implementation against `ORIGINAL_PROMPT.md`, `CLAUDE.md`, and the `README.md`.

Each task is self-contained and can be executed independently unless a dependency is noted.



## ISSUE-12 — `README.md` does not document the automatic bare-file initialisation behaviour

**File**: `README.md`

**Problem**: The `initialise_file` helper (added in Phase 8) automatically adds frontmatter to any `.md` file that is accessed but has no YAML frontmatter. This is a meaningful, non-obvious behaviour that is listed as a feature on line 11 of the README but never explained. A user who reads a bare file will find it has been silently modified, which can be surprising.

**Fix**: Add a short paragraph under "Features" or a new "Bare File Initialization" section explaining that the first access to a bare `.md` file (one without YAML frontmatter) triggers automatic frontmatter creation, and what defaults are used.
