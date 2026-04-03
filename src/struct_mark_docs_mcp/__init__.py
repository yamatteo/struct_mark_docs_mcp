from .server import create_server

# Export validation functions for external use
from .validation import to_snake


def main() -> None:
    server = create_server()
    server.run(transport="stdio")
