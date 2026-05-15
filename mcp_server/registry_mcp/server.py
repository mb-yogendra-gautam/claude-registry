"""Registry MCP server — browse and install skills/MCPs from Claude Desktop."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("registry-mcp")

from .tools import catalog, install_mcp, install_skill, manage, setup  # noqa: E402

catalog.register(mcp)
install_skill.register(mcp)
install_mcp.register(mcp)
manage.register(mcp)
setup.register(mcp)


def main_sync():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main_sync()
