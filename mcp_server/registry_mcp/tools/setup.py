"""Self-setup tool: verify and upgrade the registry MCP's own config."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .._lib import config

CANONICAL_CONFIG = {
    "command": "uvx",
    "args": [
        "--from",
        "git+https://github.com/mb-yogendra-gautam/claude-registry.git#subdirectory=mcp_server",
        "registry-mcp",
    ],
    "env": {
        "CLAUDE_REGISTRY_URL": "https://raw.githubusercontent.com/mb-yogendra-gautam/claude-registry/main"
    },
}


def register(mcp: FastMCP):

    @mcp.tool()
    async def setup_registry(registry_url: str | None = None, upgrade: bool = False) -> str:
        """Verify the registry MCP's own configuration and optionally upgrade it.

        Use this to:
        - Check if the registry MCP is properly configured for permanent use
        - Upgrade from a local/temporary install to the permanent uvx-based install
        - Update the registry URL if it changes

        Args:
            registry_url: Override the registry URL (optional). Defaults to the canonical GitHub URL.
            upgrade: Set to true to replace the current config with the canonical uvx-based config.
        """
        current_cfg = config.read_config()
        servers = current_cfg.get("mcpServers", {})
        registry_cfg = servers.get("registry")

        if registry_cfg is None:
            return json.dumps({
                "success": False,
                "error": "not_configured",
                "message": "Registry MCP entry not found in config. This is unexpected since this tool is running.",
            })

        is_uvx = (
            registry_cfg.get("command") == "uvx"
            and "git+https://github.com/mb-yogendra-gautam/claude-registry" in " ".join(registry_cfg.get("args", []))
        )

        if not upgrade:
            return json.dumps({
                "success": True,
                "is_permanent": is_uvx,
                "current_command": registry_cfg.get("command"),
                "current_registry_url": registry_cfg.get("env", {}).get("CLAUDE_REGISTRY_URL", "default"),
                "recommendation": None if is_uvx else "Run with upgrade=true to switch to the permanent uvx-based config.",
            })

        new_config = dict(CANONICAL_CONFIG)
        if registry_url:
            new_config = {**new_config, "env": {"CLAUDE_REGISTRY_URL": registry_url}}

        backup = config.add_mcp_server("registry", new_config)
        return json.dumps({
            "success": True,
            "upgraded": True,
            "backup_path": str(backup) if backup else None,
            "restart_required": True,
            "message": "Registry MCP config upgraded to permanent uvx-based install. Restart Claude Desktop.",
        })
