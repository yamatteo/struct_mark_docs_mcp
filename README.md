# struct-mark-docs-mcp

An MCP (Model Context Protocol) server for managing structured markdown documentation with YAML frontmatter, automatic reference tracking, and content validation.

## Features

- **Structure-aware editing**: Read, write, and manage markdown files by sections and subsections
- **Automatic frontmatter management**: YAML headers with title, abstracts, word counts, and TOC
- **Reference tracking**: Automatic management of cross-file references and back-references
- **Content validation**: Enforces abstract length limits and prevents heading injection
- **Pending actions**: Scan all files for missing abstracts, over-limit content, and broken references
- **Bare file initialization**: Automatically adds frontmatter to plain markdown files

## Installation

### With uv (recommended)

```bash
# Add to your project
uv add struct-mark-docs-mcp

# Or run directly with uvx
uvx struct-mark-docs-mcp
```

### Manual installation

```bash
git clone https://github.com/yamatteo/struct-mark-docs-mcp
cd struct-mark-docs-mcp
uv sync
```

## Quickstart

1. **Set your documentation directory**:
   ```bash
   export MARKDOWN_DOCS_DIR="/path/to/your/docs"
   ```

2. **Start the MCP server**:
   ```bash
   uv run struct-mark-docs-mcp
   ```

3. **Configure in Claude Desktop** (or other MCP client):
   ```json
   {
     "mcpServers": {
       "struct-mark-docs": {
         "command": "uvx",
         "args": ["struct-mark-docs-mcp"],
         "env": {
           "MARKDOWN_DOCS_DIR": "/path/to/your/docs"
         }
       }
     }
   }
   ```

## Configuration

Create a `.struct-mark.yaml` or `struct-mark.yaml` file in your documentation directory:

```yaml
description: "My project documentation"
index_file: README.md
abstract_limit_file: 380
abstract_limit_section: 288
abstract_limit_subsection: 204
abstract_limit_subsubsection: 128
section_wc_soft_limit: 800
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `description` | string | `""` | Documentation description |
| `index_file` | string | `"README.md"` | Standard index file name |
| `abstract_limit_file` | int | `380` | Max characters for file abstract |
| `abstract_limit_section` | int | `288` | Max characters for section abstract |
| `abstract_limit_subsection` | int | `204` | Max characters for subsection abstract |
| `abstract_limit_subsubsection` | int | `128` | Max characters for subsubsection abstract |
| `section_wc_soft_limit` | int | `800` | Soft word count limit for sections |

## Bare File Initialization

When a `.md` file without YAML frontmatter is accessed for the first time, the system automatically creates minimal frontmatter to make it compatible with the structured documentation system.

**What triggers initialization**: Any read operation on a bare `.md` file (one without YAML frontmatter) will automatically add frontmatter.

**Default frontmatter structure**:
```yaml
title: snake_case_filename
abstract: ""
wc: 0
toc: []
refs: []
back_refs: []
```

**Title normalization**: The filename is converted to snake_case using the pattern `re.sub(r'[^a-zA-Z0-9]+', '_', title).lower().strip('_')[:255]` to ensure consistent naming and reference handling.

**User impact**: The file is modified in-place during the first access. If you prefer to manage frontmatter manually, ensure your `.md` files include YAML frontmatter before accessing them through the MCP tools.

## Frontmatter Schema

All managed markdown files have YAML frontmatter:

```yaml
title: snake_case_filename
abstract: |
  File-level abstract (max 380 chars).
wc: 240  # Total word count of entire file body (all sections combined)
toc:
  - title: Section Title
    abstract: |
      Section abstract (max 288 chars).
    wc: 150  # Word count of section's direct body only (excludes subsections)
    subsections:
      - title: Subsection Title
        abstract: |
          Subsection abstract (max 204 chars).
        wc: 70  # Word count of subsection's direct body only (excludes subsubsections)
        subsubsections:
          - title: Subsubsection Title
            abstract: |
              Subsubsection abstract (max 128 chars).
            wc: 20  # Word count of subsubsection's direct body only
refs:
  - other_file_snake_title
back_refs:
  - parent_file_snake_title
```

## MCP Tools Reference

### File Management

#### `list_files`
List all `.md` files with word count and abstract status.

**Returns**: String with one line per file showing status.

#### `read_header`
Read the YAML frontmatter of a markdown file.

**Parameters**:
- `filename` (string): Name of the markdown file

**Returns**: YAML frontmatter as string.

#### `sync_header`
Recompute word counts, rebuild TOC, and scan references for a markdown file.

**Parameters**:
- `filename` (string): Name of the markdown file

**Returns**: Action summary and next steps.

### Abstract Management

#### `update_abstract`
Update the abstract for a file or specific section.

**Parameters**:
- `filename` (string): Name of the markdown file
- `abstract` (string): New abstract content
- `section_path` (string|optional): Path like "Section/Subsection" (omit for file-level)

**Returns**: Action confirmation and next steps.

### Section Operations

#### `read_section`
Read a section's full content by slash-separated path.

**Parameters**:
- `filename` (string): Name of the markdown file
- `section_path` (string): Path like "Introduction/Overview"

**Returns**: Section content with heading and body.

#### `write_section`
Replace a section's body (children preserved).

**Parameters**:
- `filename` (string): Name of the markdown file
- `section_path` (string): Path like "Introduction/Overview"
- `content` (string): New section body content

**Returns**: Action confirmation and next steps.

#### `add_section`
Add a new section at root or under a parent.

**Parameters**:
- `filename` (string): Name of the markdown file
- `title` (string): New section title
- `parent_path` (string|optional): Parent section path
- `position` (int|optional): Insert position (0-based)

**Returns**: Action confirmation and next steps.

#### `remove_section`
Remove a section and all its children.

**Parameters**:
- `filename` (string): Name of the markdown file
- `section_path` (string): Path like "Introduction/Overview"

**Returns**: Action confirmation and next steps.

#### `rename_section`
Rename a section and flag affected files.

**Parameters**:
- `filename` (string): Name of the markdown file
- `section_path` (string): Current section path
- `new_title` (string): New section title

**Returns**: Action confirmation and next steps.

### Actions and Status

#### `get_pending_actions`
Emit a prioritized list of pending actions across all files.

**Returns**: Formatted list of actions needed, prioritized by importance.

## Post-modification Response Format

All modifying tools return responses in this format:

```
ACTION: <description of what was done>
NEXT_STEPS:
  - update abstract for section "X" in file.md
  - update abstract for file.md (parent level)
  - consider reviewing references in: a.md, b.md
```

## Key Invariants

### Path Traversal Guard
- All file access goes through `resolve_path()` which ensures files are within `MARKDOWN_DOCS_DIR`
- Prevents access to files outside the documentation directory

### Heading Injection Prevention
- `write_section` rejects content containing ATX headings (`^#{1,6}\s`) or setext underlines
- Ensures structural integrity of the document hierarchy

### Abstract Length Limits
- File abstracts: max 380 characters
- Section abstracts: max 288 characters  
- Subsection abstracts: max 204 characters
- Subsubsection abstracts: max 128 characters
- Over-limit abstracts are rejected, not just warned

### Title Normalization
- Titles converted to snake_case: `re.sub(r'[^a-zA-Z0-9]+', '_', title).lower().strip('_')[:255]`
- Ensures consistent file naming and reference handling

### Section Levels
- Only levels 1-3 (`#`, `##`, `###`) are managed as structural elements
- Deeper levels are treated as body content within sections

### Word Count Behavior
- File-level `wc` counts total word count of entire file body (all sections combined)
- Section-level `wc` counts only the direct body text of that section, excluding nested subsections
- This means file `wc` ≠ sum of all section `wc` values (this is intentional behavior)

## Example Workflow

```bash
# 1. List all files
list_files

# 2. Check what needs attention
get_pending_actions

# 3. Add a new section
add_section(filename="guide.md", title="Getting Started")

# 4. Write section content
write_section(filename="guide.md", section_path="Getting Started", content="This is the getting started section with detailed instructions...")

# 5. Update the abstract
update_abstract(filename="guide.md", section_path="Getting Started", abstract="Quick start guide for new users")

# 6. Check for remaining tasks
get_pending_actions
```

## Development

This project uses `uv` for dependency management:

```bash
# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linting
uv run ruff check

# Run both
uv run pytest && uv run ruff check
```

## License

MIT

## Contributing

Use github issues.