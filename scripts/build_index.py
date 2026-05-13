#!/usr/bin/env python3
"""Build index.json by scanning skills/ and mcps/ directories.

Run from repo root:
    python scripts/build_index.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MCPS_DIR = REPO_ROOT / "mcps"
INDEX_PATH = REPO_ROOT / "index.json"

# Fields copied into the index. Full manifest stays in the folder; the index is
# a slim catalog so the installer can list things without downloading everything.
SKILL_INDEX_FIELDS = ("id", "name", "version", "description", "author", "tags", "license", "homepage")
MCP_INDEX_FIELDS = ("id", "name", "version", "description", "author", "tags", "license", "homepage", "runtime")


def load_manifest(folder: Path) -> dict:
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing manifest.json in {folder}")
    with manifest_path.open() as f:
        return json.load(f)


def collect(directory: Path, kind: str, fields: tuple[str, ...]) -> list[dict]:
    entries = []
    if not directory.exists():
        return entries
    for sub in sorted(directory.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        manifest = load_manifest(sub)
        if manifest["id"] != sub.name:
            raise ValueError(
                f"{kind} folder name '{sub.name}' must match manifest id '{manifest['id']}'"
            )
        entry = {k: manifest[k] for k in fields if k in manifest}
        entry["path"] = f"{directory.name}/{sub.name}"
        entries.append(entry)
    return entries


def main() -> int:
    try:
        skills = collect(SKILLS_DIR, "skill", SKILL_INDEX_FIELDS)
        mcps = collect(MCPS_DIR, "mcp", MCP_INDEX_FIELDS)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    index = {
        "version": "1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skills": skills,
        "mcps": mcps,
    }
    with INDEX_PATH.open("w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")
    print(f"wrote {INDEX_PATH} ({len(skills)} skills, {len(mcps)} mcps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
