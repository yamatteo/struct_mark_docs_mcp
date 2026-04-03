---
title: Getting Started Guide
abstract: |
  Comprehensive getting started guide for new users of the structured markdown documentation system. This guide covers installation, configuration, and basic usage patterns to help you become productive quickly.
wc: 420
toc:
  - title: Installation
    abstract: |
      Step-by-step installation instructions for different platforms and environments, including prerequisites and troubleshooting common installation issues.
    wc: 180
    subsections:
      - title: System Requirements
        abstract: |
          Detailed system requirements and compatibility information for various platforms.
        wc: 60
      - title: Platform-Specific Instructions
        abstract: |
          Installation instructions tailored for different operating systems and environments.
        wc: 70
      - title: Verification
        abstract: |
          How to verify that the installation was successful and the system is working correctly.
        wc: 50
  - title: Initial Configuration
    abstract: |
      Guide to initial configuration setup, including creating the configuration file and setting up basic options.
    wc: 140
    subsections:
      - title: Creating Configuration File
        abstract: |
          How to create and customize the docs_config.yaml file for your project.
        wc: 45
      - title: Basic Settings
        abstract: |
          Overview of essential configuration settings and their recommended values.
        wc: 55
      - title: Advanced Options
        abstract: |
          Introduction to advanced configuration options for power users.
        wc: 40
  - title: First Steps
    abstract: |
      Your first steps with the system, creating your first structured document and understanding the workflow.
    wc: 100
refs:
  - api_reference
  - best_practices
  - troubleshooting_guide
  - index
back_refs:
  - index
---

# Installation

Installing the structured markdown documentation system is straightforward process that varies slightly depending on your platform and environment.

## System Requirements

Before installing the system, ensure your environment meets the following requirements:

- **Python**: Version 3.8 or higher
- **Package Manager**: `uv` for dependency management
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 512MB RAM available
- **Storage**: 100MB free disk space

## Platform-Specific Instructions

Follow the platform-specific instructions below for your operating system:

### Linux and macOS

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the documentation system
uv install struct-mark-docs-mcp
```

### Windows

```powershell
# Install uv using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install the documentation system
uv install struct-mark-docs-mcp
```

## Verification

After installation, verify that the system is working correctly:

```bash
# Check installation
uv run struct-mark-docs-mcp --version

# Run basic functionality test
uv run struct-mark-docs-mcp --test
```

# Initial Configuration

Proper configuration is essential for getting the most out of the documentation system.

## Creating Configuration File

Create a `docs_config.yaml` file in your documentation directory with the following basic structure:

```yaml
description: "Your documentation description"
index_file: "_index.md"
content_directory: "./content"
```

## Basic Settings

Configure the essential settings to match your project requirements:

- **Description**: Brief description of your documentation project
- **Index File**: Name of your main index file (usually `_index.md`)
- **Content Directory**: Directory containing your markdown files

## Advanced Options

For advanced users, the system offers numerous configuration options:

- Custom validation rules
- Automated content generation settings
- Integration with external tools
- Custom metadata fields

# First Steps

With the system installed and configured, you're ready to create your first structured document.

1. Create your content directory if it doesn't exist
2. Create your main index file with proper YAML headers
3. Add content following the structured format
4. Let the system manage metadata and references automatically

The system will automatically track word counts, validate structure, and maintain cross-references as you work.
