from .server import create_server


def main() -> None:
    server = create_server()
    server.run(transport="stdio")
