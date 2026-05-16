"""Skill installation tool."""
from __future__ import annotations

import json
import shutil

from mcp.server.fastmcp import FastMCP

from .._lib import packaging, paths, registry, state


def _files_to_install(manifest: dict) -> list[str]:
    if "files" in manifest:
        return manifest["files"]
    return [manifest.get("entrypoint", "SKILL.md")]


def register(mcp: FastMCP):

    @mcp.tool()
    async def install_skill(skill_id: str, platform: str = "cli", force: bool = False) -> str:
        """Download and install a skill from the registry.

        Behavior depends on the target platform:
        - "desktop": Saves the skill as a zip file in the user's Downloads folder
          for manual import into Claude Desktop.
        - "cli": Installs the skill directly to the local Claude skills directory.

        Use platform="desktop" when the user asks to install for Claude Desktop.
        Use platform="cli" when installing for Claude Code CLI or general use.

        Args:
            skill_id: The skill identifier (e.g. "pdf-summarizer").
            platform: Target platform — "desktop" or "cli".
            force: Set to true to overwrite if already installed/exists.
        """
        try:
            entries = registry.fetch_index()
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        entry = registry.find_entry(entries, "skill", skill_id)
        if not entry:
            return json.dumps({"success": False, "error": "not_found",
                               "message": f"Skill '{skill_id}' not found in registry."})

        try:
            manifest = registry.fetch_manifest(entry.path)
        except Exception as e:
            return json.dumps({"success": False, "error": "network_error", "message": str(e)})

        if platform == "desktop":
            return _install_desktop(entry, manifest, skill_id, force)

        return _install_cli(entry, manifest, skill_id, force)


def _install_desktop(entry, manifest: dict, skill_id: str, force: bool) -> str:
    downloads = paths.downloads_dir()
    zip_path = downloads / f"{skill_id}.zip"

    if zip_path.exists() and not force:
        return json.dumps({
            "success": False,
            "error": "already_exists",
            "message": f"File '{zip_path}' already exists. Set force=true to overwrite.",
        })

    try:
        zip_bytes, included_files = packaging.build_skill_zip(entry, manifest)
    except Exception as e:
        return json.dumps({"success": False, "error": "download_error", "message": str(e)})

    try:
        downloads.mkdir(parents=True, exist_ok=True)
        zip_path.write_bytes(zip_bytes)
    except Exception as e:
        return json.dumps({"success": False, "error": "write_error",
                           "message": f"Failed to save zip: {e}"})

    skills_dir = paths.claude_skills_dir()
    return json.dumps({
        "success": True,
        "skill_id": skill_id,
        "version": manifest["version"],
        "saved_to": str(zip_path),
        "files_included": included_files,
        "size_bytes": len(zip_bytes),
        "instructions": (
            f"The skill has been saved as a zip file to {zip_path}. "
            f"To complete installation, extract the zip contents to "
            f"{skills_dir}/{skill_id}/ and restart Claude Desktop."
        ),
    })


def _install_cli(entry, manifest: dict, skill_id: str, force: bool) -> str:
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
