"""Skill installation tool."""
from __future__ import annotations

import json
import shutil

from mcp.server.fastmcp import FastMCP

from .._lib import paths, registry, state


def _files_to_install(manifest: dict) -> list[str]:
    if "files" in manifest:
        return manifest["files"]
    return [manifest.get("entrypoint", "SKILL.md")]


def register(mcp: FastMCP):

    @mcp.tool()
    async def install_skill(skill_id: str, force: bool = False) -> str:
        """Download and install a skill from the registry to the local Claude skills directory.

        Args:
            skill_id: The skill identifier (e.g. "pdf-summarizer").
            force: Set to true to overwrite if already installed.
        """
        try:
            entries = registry.fetch_index()
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        entry = registry.find_entry(entries, "skill", skill_id)
        if not entry:
            return json.dumps({"success": False, "error": "not_found", "message": f"Skill '{skill_id}' not found in registry."})

        try:
            manifest = registry.fetch_manifest(entry.path)
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        dest = paths.claude_skills_dir() / skill_id
        if dest.exists() and not force:
            return json.dumps({
                "success": False,
                "error": "already_installed",
                "message": f"Skill '{skill_id}' is already installed at {dest}. Set force=true to overwrite.",
            })

        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True, exist_ok=True)

        files = _files_to_install(manifest)
        installed_files = []
        try:
            for rel in files:
                content = registry.fetch_file(entry.path, rel)
                target = dest / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                installed_files.append(rel)
        except Exception as e:
            shutil.rmtree(dest, ignore_errors=True)
            return json.dumps({"success": False, "error": "download_error", "message": str(e)})

        state.record("skill", skill_id, manifest["version"], {"dest": str(dest)})

        return json.dumps({
            "success": True,
            "skill_id": skill_id,
            "version": manifest["version"],
            "installed_path": str(dest),
            "files": installed_files,
            "restart_required": True,
        })
