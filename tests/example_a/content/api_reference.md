---
title: Api Reference
abstract: |
  Complete API reference documentation for the structured markdown documentation MCP server. This document covers all available tools, their parameters, and usage examples for integration with various applications.
wc: 680
toc:
  - title: Core API Tools
    abstract: |
      Reference documentation for the core API tools that form the foundation of the structured markdown documentation system.
    wc: 250
    subsections:
      - title: File Management Tools
        abstract: |
          Tools for creating, reading, updating, and deleting markdown files with automatic metadata management.
        wc: 80
      - title: Metadata Operations
        abstract: |
          Operations for managing YAML headers, abstracts, table of contents, and cross-references.
        wc: 75
      - title: Content Structure Tools
        abstract: |
          Tools for modifying document structure, adding/removing sections, and reorganizing content hierarchy.
        wc: 95
  - title: Validation Tools
    abstract: |
      Tools for validating document structure, checking metadata compliance, and ensuring consistency across the documentation set.
    wc: 180
    subsections:
      - title: Structure Validation
        abstract: |
          Validation of document hierarchy, section nesting, and proper markdown formatting.
        wc: 60
      - title: Metadata Validation
        abstract: |
          Checking YAML header validity, abstract length limits, and required metadata fields.
        wc: 65
      - title: Reference Validation
        abstract: |
          Validation of cross-references, back-references, and detection of circular dependencies.
        wc: 55
  - title: Utility Functions
    abstract: |
      Miscellaneous utility functions for common tasks like word counting, character counting, and content analysis.
    wc: 150
    subsections:
      - title: Content Analysis
        abstract: |
          Tools for analyzing content density, readability, and structure complexity.
        wc: 50
      - title: Statistics Tools
        abstract: |
          Functions for generating documentation statistics, progress tracking, and usage metrics.
        wc: 55
      - title: Export Functions
        abstract: |
          Tools for exporting documentation in various formats and creating custom reports.
        wc: 45
  - title: Integration Examples
    abstract: |
      Practical examples of integrating the API with various tools and workflows, including code samples and best practices.
    wc: 100
refs:
  - best_practices
  - getting_started_guide
  - troubleshooting_guide
  - index
back_refs:
  - index
  - getting_started_guide
---

# Core API Tools

The core API tools provide the fundamental operations for working with structured markdown documentation.

## File Management Tools

These tools handle the basic file operations while maintaining proper metadata and structure.

### create_document

Creates a new markdown document with automatic YAML header generation.

**Parameters:**
- `filename`: Name of the file to create
- `title`: Document title (optional, auto-generated from filename)
- `abstract`: Document abstract (optional)
- `directory`: Target directory (optional, uses configured content directory)

**Example:**
```python
result = create_document(
    filename="user_guide.md",
    title="User Guide",
    abstract="Comprehensive guide for end users"
)
```

### read_document

Reads a markdown document and returns both content and parsed metadata.

**Parameters:**
- `filename`: Name of the file to read
- `include_metadata`: Whether to include YAML header in response
- `section_filter`: Optional filter to read specific sections only

### update_document

Updates an existing document while preserving metadata structure.

## Metadata Operations

These tools manage the YAML headers and associated metadata.

### update_abstract

Updates the abstract of a document while respecting character limits.

### update_toc

Updates the table of contents structure based on document content.

### manage_references

Automatically manages references and back-references between documents.

## Content Structure Tools

Tools for modifying the hierarchical structure of documents.

### add_section

Adds a new section to a document at the specified level.

### remove_section

Removes a section and all its subsections.

### reorder_sections

Reorders sections within a document.

# Validation Tools

Validation tools ensure document quality and consistency.

## Structure Validation

Validates the hierarchical structure of documents.

### validate_hierarchy

Ensures proper nesting of sections, subsections, and subsubsections.

### check_formatting

Validates markdown formatting and prevents improper header usage.

## Metadata Validation

Validates YAML headers and associated metadata.

### validate_yaml

Checks YAML syntax and required fields.

### check_limits

Validates abstract length limits and word count constraints.

## Reference Validation

Maintains the integrity of cross-references.

### validate_references

Ensures all referenced documents exist and are accessible.

### detect_circular_refs

Prevents circular reference dependencies.

# Utility Functions

Helper functions for common documentation tasks.

## Content Analysis

Tools for analyzing document content and structure.

### analyze_readability

Calculates readability scores and content complexity metrics.

### check_density

Analyzes content density and information distribution.

## Statistics Tools

Functions for generating documentation statistics.

### generate_stats

Creates comprehensive statistics for the documentation set.

### track_progress

Monitors documentation progress and completion metrics.

## Export Functions

Tools for exporting documentation in various formats.

### export_html

Exports documentation as a static HTML website.

### export_pdf

Generates PDF versions of documentation.

# Integration Examples

## Python Integration

```python
from struct_mark_docs_mcp import DocumentationClient

client = DocumentationClient(config_path="docs_config.yaml")

# Create a new document
doc = client.create_document("api_guide.md", title="API Guide")

# Update content
client.update_content(doc.id, "# API Guide\n\nContent here...")

# Validate structure
validation = client.validate_document(doc.id)
```

## CLI Integration

```bash
# Create new document
struct-mark-docs create --filename "guide.md" --title "User Guide"

# Validate all documents
struct-mark-docs validate --all

# Generate statistics
struct-mark-docs stats --format json
```

## MCP Server Integration

The MCP server provides tools for integration with AI assistants and automated workflows. All tools are designed to work seamlessly with the MCP protocol while maintaining proper documentation structure.
