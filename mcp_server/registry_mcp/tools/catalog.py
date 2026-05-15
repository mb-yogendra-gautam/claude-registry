"""Catalog browsing tools: list, search, show details."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .._lib import registry, state


def register(mcp: FastMCP):

    @mcp.tool()
    async def list_catalog(kind: str = "all") -> str:
        """List all available skills and MCP servers in the registry.

        Args:
            kind: Filter by type — "all", "skill", or "mcp".
        """
        try:
            entries = registry.fetch_index()
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        installed = state.load()
        items = []
        for entry in entries:
            if kind != "all" and entry.kind != kind:
                continue
            is_installed = entry.id in installed.get(f"{entry.kind}s", {})
            items.append({
                "id": entry.id,
                "kind": entry.kind,
                "name": entry.name,
                "version": entry.version,
                "description": entry.description,
                "tags": entry.raw.get("tags", []),
                "installed": is_installed,
            })

        return json.dumps({"success": True, "items": items, "total_count": len(items)})

    @mcp.tool()
    async def search_catalog(query: str, kind: str = "all") -> str:
        """Search the registry by keyword. Matches against name, description, tags, and id.

        Args:
            query: Search term (case-insensitive).
            kind: Filter by type — "all", "skill", or "mcp".
        """
        try:
            entries = registry.fetch_index()
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        q = query.lower()
        installed = state.load()
        matches = []

        for entry in entries:
            if kind != "all" and entry.kind != kind:
                continue
            searchable = " ".join([
                entry.id,
                entry.name,
                entry.description,
                " ".join(entry.raw.get("tags", [])),
            ]).lower()
            if q in searchable:
                is_installed = entry.id in installed.get(f"{entry.kind}s", {})
                matches.append({
                    "id": entry.id,
                    "kind": entry.kind,
                    "name": entry.name,
                    "version": entry.version,
                    "description": entry.description,
                    "tags": entry.raw.get("tags", []),
                    "installed": is_installed,
                })

        return json.dumps({"success": True, "matches": matches, "count": len(matches)})

    @mcp.tool()
    async def show_details(id: str, kind: str) -> str:
        """Get full details about a specific skill or MCP, including required environment variables and installation status.

        Args:
            id: The identifier of the skill or MCP (e.g. "pdf-summarizer", "github-mcp").
            kind: Either "skill" or "mcp".
        """
        try:
            entries = registry.fetch_index()
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        entry = registry.find_entry(entries, kind, id)
        if not entry:
            return json.dumps({"success": False, "error": "not_found", "message": f"{kind} '{id}' not found in registry."})

        try:
            manifest = registry.fetch_manifest(entry.path)
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        installed_state = state.load()
        bucket = installed_state.get(f"{kind}s", {})
        is_installed = id in bucket
        installed_version = bucket[id]["version"] if is_installed else None

        result = {
            "success": True,
            "manifest": manifest,
            "is_installed": is_installed,
            "installed_version": installed_version,
        }
        return json.dumps(result)
