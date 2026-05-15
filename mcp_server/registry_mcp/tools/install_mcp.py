"""MCP installation tool."""
from __future__ import annotations

import copy
import json

from mcp.server.fastmcp import FastMCP

from .._lib import config, paths, registry, state

PROTECTED_IDS = {"registry"}


def _substitute(template: dict, values: dict[str, str]) -> dict:
    result = copy.deepcopy(template)

    def sub(s):
        if isinstance(s, str) and s.startswith("<") and s.endswith(">"):
            key = s[1:-1]
            if key in values:
                return values[key]
        return s

    if "env" in result:
        result["env"] = {k: sub(v) for k, v in result["env"].items()}
    if "args" in result:
        result["args"] = [sub(a) for a in result["args"]]
    return result


def register(mcp: FastMCP):

    @mcp.tool()
    async def install_mcp_server(mcp_id: str, env_values: dict | None = None, force: bool = False, use_placeholders: bool = False) -> str:
        """Install an MCP server by adding its configuration to claude_desktop_config.json.

        If the MCP requires environment variables (API keys, paths), provide them in env_values.
        Call show_details first to see what variables are needed.

        Alternatively, set use_placeholders=true to install without providing env values.
        Placeholders will remain in the config for the user to fill in manually.

        Args:
            mcp_id: The MCP identifier (e.g. "github-mcp").
            env_values: Key-value pairs for required environment variables. Keys must match the required_env names from the manifest.
            force: Set to true to overwrite an existing MCP config with the same id.
            use_placeholders: Set to true to install with placeholder values. The user must edit the config file manually before the MCP will work.
        """
        if env_values is None:
            env_values = {}

        if mcp_id in PROTECTED_IDS:
            return json.dumps({
                "success": False,
                "error": "protected",
                "message": f"Cannot modify the '{mcp_id}' MCP — it is protected.",
            })

        try:
            entries = registry.fetch_index()
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        entry = registry.find_entry(entries, "mcp", mcp_id)
        if not entry:
            return json.dumps({"success": False, "error": "not_found", "message": f"MCP '{mcp_id}' not found in registry."})

        try:
            manifest = registry.fetch_manifest(entry.path)
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        if config.has_mcp_server(mcp_id) and not force:
            return json.dumps({
                "success": False,
                "error": "already_configured",
                "message": f"MCP '{mcp_id}' is already configured. Set force=true to replace it.",
            })

        required_env = manifest.get("required_env", [])
        missing = []
        for spec in required_env:
            name = spec["name"]
            if name not in env_values:
                missing.append({
                    "name": name,
                    "description": spec.get("description", ""),
                    "example": spec.get("example"),
                    "secret": spec.get("secret", False),
                })

        if missing and not use_placeholders:
            return json.dumps({
                "success": False,
                "error": "missing_env_values",
                "message": "Required environment variables are missing. Provide them via env_values, or set use_placeholders=true to install with placeholder values.",
                "required": missing,
            })

        server_config = _substitute(manifest["config_template"], env_values)
        backup = config.add_mcp_server(mcp_id, server_config)
        state.record("mcp", mcp_id, manifest["version"])

        result = {
            "success": True,
            "mcp_id": mcp_id,
            "version": manifest["version"],
            "config_added": True,
            "backup_path": str(backup) if backup else None,
            "restart_required": True,
        }

        if missing:
            config_path = str(paths.claude_config_file())
            result["placeholders_used"] = True
            result["pending_configuration"] = missing
            result["instructions"] = (
                f"The MCP server '{mcp_id}' has been added to your config with placeholder values. "
                f"Before it will work, edit {config_path} and replace: "
                + ", ".join(f"<{m['name']}>" for m in missing)
                + " with actual values."
            )
        else:
            result["placeholders_used"] = False

        return json.dumps(result)
