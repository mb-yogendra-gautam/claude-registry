"""Management tools: list installed, uninstall."""
from __future__ import annotations

import json
import shutil

from mcp.server.fastmcp import FastMCP

from .._lib import config, paths, state

PROTECTED_IDS = {"registry"}


def register(mcp: FastMCP):

    @mcp.tool()
    async def list_installed() -> str:
        """Show all currently installed skills and MCP servers, with their versions and install dates."""
        installed = state.load()
        return json.dumps({"success": True, **installed})

    @mcp.tool()
    async def uninstall(id: str, kind: str) -> str:
        """Uninstall a skill or MCP server.

        Args:
            id: The identifier to uninstall (e.g. "pdf-summarizer", "github-mcp").
            kind: Either "skill" or "mcp".
        """
        if kind == "mcp" and id in PROTECTED_IDS:
            return json.dumps({
                "success": False,
                "error": "protected",
                "message": f"Cannot uninstall the '{id}' MCP — it is protected.",
            })

        if kind == "skill":
            installed = state.load()
            if id not in installed.get("skills", {}):
                return json.dumps({"success": False, "error": "not_installed", "message": f"Skill '{id}' is not installed."})
            dest = paths.claude_skills_dir() / id
            if dest.exists():
                shutil.rmtree(dest)
            state.forget("skill", id)
            return json.dumps({"success": True, "message": f"Skill '{id}' uninstalled.", "restart_required": True})

        elif kind == "mcp":
            removed, backup = config.remove_mcp_server(id)
            if not removed:
                return json.dumps({"success": False, "error": "not_configured", "message": f"MCP '{id}' is not in config."})
            state.forget("mcp", id)
            return json.dumps({
                "success": True,
                "message": f"MCP '{id}' removed from config.",
                "backup_path": str(backup) if backup else None,
                "restart_required": True,
            })

        return json.dumps({"success": False, "error": "invalid_kind", "message": "kind must be 'skill' or 'mcp'."})
