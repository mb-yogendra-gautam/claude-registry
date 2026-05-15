"""Skill zip export tool."""
from __future__ import annotations

import base64
import io
import json
import zipfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .._lib import registry


def _files_to_export(manifest: dict) -> list[str]:
    if "files" in manifest:
        return manifest["files"]
    return [manifest.get("entrypoint", "SKILL.md")]


def register(mcp: FastMCP):

    @mcp.tool()
    async def export_skill_zip(skill_id: str, output_path: str | None = None) -> str:
        """Export a skill from the registry as a base64-encoded zip file.

        Use this when the user wants to download a skill as a zip archive
        for manual import into Claude Desktop or sharing.

        Args:
            skill_id: The skill identifier (e.g. "csv-cleaner").
            output_path: Optional file path to write the zip to (e.g. "~/Downloads/csv-cleaner.zip").
                         If provided, the zip is also saved to this location.
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

        files = _files_to_export(manifest)
        buf = io.BytesIO()
        included_files = []
        try:
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for rel in files:
                    content = registry.fetch_file(entry.path, rel)
                    arcname = f"{skill_id}/{rel}"
                    zf.writestr(arcname, content)
                    included_files.append(rel)
        except Exception as e:
            return json.dumps({"success": False, "error": "download_error", "message": str(e)})

        zip_bytes = buf.getvalue()
        zip_b64 = base64.b64encode(zip_bytes).decode("ascii")

        saved_path = None
        if output_path:
            try:
                dest = Path(output_path).expanduser().resolve()
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zip_bytes)
                saved_path = str(dest)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": "write_error",
                    "message": f"Zip created but failed to write to {output_path}: {e}",
                    "zip_base64": zip_b64,
                })

        return json.dumps({
            "success": True,
            "skill_id": skill_id,
            "version": manifest["version"],
            "filename": f"{skill_id}.zip",
            "files_included": included_files,
            "zip_base64": zip_b64,
            "size_bytes": len(zip_bytes),
            "saved_to": saved_path,
            "instructions": "Save this zip file and import it into Claude Desktop, or extract it to your skills directory.",
        })
