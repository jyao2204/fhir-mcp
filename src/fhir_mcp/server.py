from mcp.server import MCPServer

server = MCPServer("fhir-mcp")

@server.tool()
def ping() -> str:
    """Tool to check if server is alive and able to respond."""
    return "Server is live and operational."


if __name__ == "__main__":
    server.run()