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

    return mcp
