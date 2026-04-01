import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP

from .config import DocsConfig, load_config
from .exceptions import ConfigError
from .ops.abstract_ops import update_abstract as update_abstract_op
from .ops.header_ops import read_header as read_header_op
from .ops.header_ops import sync_header as sync_header_op
from .ops.list_ops import list_files as list_files_op
from .ops.section_ops import add_section as add_section_op
from .ops.section_ops import read_section as read_section_op
from .ops.section_ops import remove_section as remove_section_op
from .ops.section_ops import rename_section as rename_section_op
from .ops.section_ops import write_section as write_section_op


@dataclass
class AppState:
    docs_dir: Path
    config: DocsConfig


@asynccontextmanager
async def lifespan(app: FastMCP):
    docs_dir = Path(os.environ.get("MARKDOWN_DOCS_DIR", ".")).resolve()
    try:
        config = load_config(docs_dir)
    except ConfigError:
        config = DocsConfig()
    yield AppState(docs_dir=docs_dir, config=config)


def create_server() -> FastMCP:
    mcp = FastMCP("struct-mark-docs", lifespan=lifespan)

    @mcp.tool()
    def list_files(ctx: Context) -> str:
        """List all .md files with wc and abstract status."""
        state: AppState = ctx.request_context.lifespan_context
        return list_files_op(state.docs_dir, state.config)

    @mcp.tool()
    def read_header(filename: str, ctx: Context) -> str:
        """Read the YAML frontmatter of a markdown file."""
        state: AppState = ctx.request_context.lifespan_context
        return read_header_op(state.docs_dir, filename)

    @mcp.tool()
    def sync_header(filename: str, ctx: Context) -> str:
        """Recompute wc, rebuild toc, scan refs for a markdown file."""
        state: AppState = ctx.request_context.lifespan_context
        return sync_header_op(state.docs_dir, state.config, filename)

    @mcp.tool()
    def update_abstract(
        filename: str, abstract: str, section_path: str | None, ctx: Context
    ) -> str:
        """Update the abstract for a file or a section/subsection/subsubsection."""
        state: AppState = ctx.request_context.lifespan_context
        return update_abstract_op(state.docs_dir, state.config, filename, abstract, section_path)

    @mcp.tool()
    def read_section(filename: str, section_path: str, ctx: Context) -> str:
        """Read a section's full content by slash-separated path."""
        state: AppState = ctx.request_context.lifespan_context
        return read_section_op(state.docs_dir, filename, section_path)

    @mcp.tool()
    def write_section(filename: str, section_path: str, content: str, ctx: Context) -> str:
        """Replace a section's body (children preserved); rejects heading injection."""
        state: AppState = ctx.request_context.lifespan_context
        return write_section_op(state.docs_dir, state.config, filename, section_path, content)

    @mcp.tool()
    def add_section(
        filename: str,
        title: str,
        ctx: Context,
        parent_path: str | None = None,
        position: int | None = None,
    ) -> str:
        """Add a new section at root or under a parent section."""
        state: AppState = ctx.request_context.lifespan_context
        return add_section_op(state.docs_dir, state.config, filename, title, parent_path, position)

    @mcp.tool()
    def remove_section(filename: str, section_path: str, ctx: Context) -> str:
        """Remove a section and all its children."""
        state: AppState = ctx.request_context.lifespan_context
        return remove_section_op(state.docs_dir, state.config, filename, section_path)

    @mcp.tool()
    def rename_section(
        filename: str, section_path: str, new_title: str, ctx: Context
    ) -> str:
        """Rename a section; check other files for refs to the old title."""
        state: AppState = ctx.request_context.lifespan_context
        return rename_section_op(state.docs_dir, state.config, filename, section_path, new_title)

    return mcp
