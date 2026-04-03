class DocsMCPError(Exception):
    """Base exception for all struct-mark-docs-mcp errors."""


class ConfigError(DocsMCPError):
    """Configuration file loading or parsing failure."""


class DocsFileNotFoundError(DocsMCPError):
    """Requested file not found within docs directory."""


class ValidationError(DocsMCPError):
    """Input fails validation (abstract too long, invalid title, etc.)."""


class InjectionError(DocsMCPError):
    """Section body contains forbidden heading markers."""


class SectionNotFoundError(DocsMCPError):
    """Section path does not match any section in file."""


class DuplicateSectionError(DocsMCPError):
    """A section with this title already exists at the same level."""
