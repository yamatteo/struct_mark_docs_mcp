# ISSUE N. xx

## Issue status

Open, confirmed, etc..

## Issue content

Issue as reported by the user.

## Proposed confirmation test

Starts empty

## Proposed solution

Starts empty

## Implemented solution

.

---

# ISSUE N. 1

## Issue status

Open

## Issue content

Documentation misplaced: In the main README.md there is a section about "Bare File Initialization" even before "Installation" and "Quick start". This is misplaced and needs to go lower in the document.

## Proposed confirmation test

1. Open README.md file
2. Verify that "Bare File Initialization" section appears before "Installation" section
3. Verify that "Bare File Initialization" section appears before "Quick start" section
4. Confirm this creates confusion for users trying to follow the documentation in logical order

## Proposed solution

Move the "Bare File Initialization" section from line 14 to after the "Quickstart" section (around line 80). This creates a logical flow:

1. Features (what it does)
2. Installation (how to install)  
3. Quickstart (how to start using)
4. Configuration (how to configure)
5. Bare File Initialization (advanced behavior explanation)

**Implementation steps:**
1. Cut lines 14-33 (Bare File Initialization section)
2. Paste after line 79 (after Configuration section)
3. Update section order to maintain logical flow for new users

## Implemented solution

**COMPLETED**: Successfully moved "Bare File Initialization" section from line 14 to line 87 (after Configuration section).

**Changes made:**
1. Removed "Bare File Initialization" section (lines 14-33) from before "Installation"
2. Inserted the section after "Configuration" section (now at line 87)
3. Updated documentation flow to logical order:
   - Features → Installation → Quickstart → Configuration → Bare File Initialization → Frontmatter Schema

**Verification:**
- Installation now appears at line 14 (before Bare File Initialization)
- Quickstart appears at line 34 (before Bare File Initialization)  
- Configuration appears at line 60 (before Bare File Initialization)
- Bare File Initialization now appears at line 87 (after all setup sections)

The documentation now follows a user-friendly progression for new users.

---

# ISSUE N. 2

## Issue status

Open

## Issue content

Wrong installation instructions: If I try to follow the recommended installation instructions I get an error:

```bash
yamatteo@yamatteo-ThinkPad-T490s:/tmp$ uv init test
Initialized project `test` at `/tmp/test`
yamatteo@yamatteo-ThinkPad-T490s:/tmp$ cd test/
yamatteo@yamatteo-ThinkPad-T490s:/tmp/test$ uv add struct-mark-docs-mcp
Using CPython 3.13.7 interpreter at: /usr/bin/python3.13
Creating virtual environment at: .venv
  × No solution found when resolving dependencies:
  ╰─▶ Because struct-mark-docs-mcp was not found in the package registry and your project depends on
      struct-mark-docs-mcp, we can conclude that your project's requirements are unsatisfiable.
  help: If you want to add the package regardless of the failed resolution, provide the `--frozen` flag to skip
        locking and syncing.
yamatteo@yamatteo-ThinkPad-T490s:/tmp/test$ uvx struct-mark-docs-mcp
  × No solution found when resolving tool dependencies:
  ╰─▶ Because struct-mark-docs-mcp was not found in the package registry and you require struct-mark-docs-mcp, we
      can conclude that your requirements are unsatisfiable.
yamatteo@yamatteo-ThinkPad-T490s:/tmp/test$ 
```

## Proposed confirmation test

Starts empty

## Proposed solution

Starts empty

## Implemented solution

.
