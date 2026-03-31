import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .config import DocsConfig, load_config
from .exceptions import ConfigError


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
    return mcp
