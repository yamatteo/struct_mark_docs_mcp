I want to build an MCP for handling markdown documentation. I'll list a few requirements, we'll discuss implementation details and features, then you'll plan to implement it. Write the plan in the form of a file `CLAUDE.md` in the project root. Part of the plan will be a detailed todo list of the implementation steps to be executed later. Write general rules and guidance in the same file, including: this is a `uv` managed package, every python invocation goes through `uv run`; each development iteration should be tested with `uv run pytest` and `uv run ruff check`; each development iteration should be small and committed with git.

## Requirements
- All docs reside in a single directory that the user can configure via environment variable `MARKDOWN_DOCS_DIR` from the project he is using the MCP from: the server will be started from the docs root and will be able to access, read and modify only markdown file in that directory or its subdirectories.
- The MCP should be able to list all markdown files in the directory
- There will be a yaml configuration file in that same directory that will contain the configuration for the MCP, including:
  - Description of the documentation structure
  - standard index file name, like `README.md` or `_index.md`
  - soft limits for abstracts characters counts and (sub)sections content word counts
  - anything else that might be useful
- All managed markdown files will have yaml headers with metadata, including:
  - Title correponging to the file name (transformed to snake_case)
  - Abstract (max 380 characters)
  - Toc with sections #, subsections ##, subsubsections ###
  - a list of references to other markdown files in the documentation cited in the text
  - a list of back-references to other markdown files in the documentation that cite this file
  - something like this:
    ```
    title: Yaml header template
    abstract: |
      This is the abstract (max 380 characters).
    wc: 240
    toc:
      - title: Introduction
        abstract: |
          This is the introduction section (max 288 characters).
        wc: 150
        subsections:
          - title: Overview
            abstract: |
              This is the overview subsection (max 204 characters).
            wc: 70
          - title: Getting Started
            abstract: |
              This is the getting started subsection (max 204 characters).
            wc: 65
            subsubsections:
              - title: Installation
                abstract: |
                  This is the installation subsection (max 128 characters).
                wc: 20
              - title: Configuration
                abstract: |
                  This is the configuration subsection (max 128 characters).
                wc: 25
      - title: Conclusion
        abstract: |
          This is the conclusion section (max 288 characters).
        wc: 80
    refs:
      - other_file_snake_case_title
    back_refs:
      - parent_file_snake_case_title
    ```
  - characters and word counts for each section, subsection and subsubsection, and for the whole file
  - whatever else might be useful
- the MCP will interact with the running agent to update abstracts and toc based on the content of the markdown files
- the MCP will have tool to read and modify abstract and tocs of markdown files
- the MCP will have tool to read and modify the content of markdown files that are structure aware: you can ask to read a specific section or subsection
- the MCP will have tool to modify the structure of the documentation: add, remove, rename sections and subsections
- the MCP will prevent injection of section, subsection or subsubsection markers in the content of the markdown files
- when a section or subsection is modified, the MCP will ask the calling agent to update the abstract, eventually updating the parent section or subsection abstract
- the MCP will refuse abstracts that are too long with respect to the allowed character limit
- when a section or subsection is modified, the MCP will update the word count of the section and its parent section or subsection
- titles that can't be file name will be escaped: each character that is not alphanumeric or underscore will be replaced by an underscore, and the title will be truncated to 255 characters; duplicate titles will be refused as well as duplicate section headers
- the MCP will manage references and backreferences automatically
- upon modification of a file, the MCP ask the running agent what other file needs a modification, suggesting revision of references and backreferences
- the MCP can be asked to emit a list of actions to be performed by the agent for the tasks that require language understanding and cannot be automated: for example, to write/review abstracts, to cross-compare sections, to evaluate content shortening/split for excessive word counts