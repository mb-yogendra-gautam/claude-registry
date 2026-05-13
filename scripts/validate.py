#!/usr/bin/env python3
"""Validate every skill and MCP manifest in the registry.

Exits non-zero on any failure. Used in CI and locally before commits.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schema"
SKILLS_DIR = REPO_ROOT / "skills"
MCPS_DIR = REPO_ROOT / "mcps"


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def validate_folder(folder: Path, schema: dict, kind: str, errors: list[str]) -> None:
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        errors.append(f"{kind} '{folder.name}': missing manifest.json")
        return

    try:
        manifest = load_json(manifest_path)
    except json.JSONDecodeError as e:
        errors.append(f"{kind} '{folder.name}': invalid JSON — {e}")
        return

    try:
        jsonschema.validate(manifest, schema)
    except jsonschema.ValidationError as e:
        errors.append(f"{kind} '{folder.name}': schema violation — {e.message}")
        return

    # id must match folder name. This is what lets the installer find things.
    if manifest["id"] != folder.name:
        errors.append(
            f"{kind} '{folder.name}': id '{manifest['id']}' does not match folder name"
        )

    # For skills, verify the entrypoint file actually exists.
    if kind == "skill":
        entrypoint = folder / manifest.get("entrypoint", "SKILL.md")
        if not entrypoint.exists():
            errors.append(f"skill '{folder.name}': entrypoint {entrypoint.name} not found")

        # Verify every listed file exists.
        for rel in manifest.get("files", []):
            if not (folder / rel).exists():
                errors.append(f"skill '{folder.name}': listed file '{rel}' not found")

    # For MCPs, basic sanity on config_template + required_env consistency.
    if kind == "mcp":
        template = manifest.get("config_template", {})
        required_env = {e["name"] for e in manifest.get("required_env", [])}
        # Find <PLACEHOLDER> tokens in template
        used_placeholders: set[str] = set()
        for v in template.get("env", {}).values():
            if isinstance(v, str) and v.startswith("<") and v.endswith(">"):
                used_placeholders.add(v[1:-1])
        for arg in template.get("args", []):
            if isinstance(arg, str) and arg.startswith("<") and arg.endswith(">"):
                used_placeholders.add(arg[1:-1])
        missing = used_placeholders - required_env
        if missing:
            errors.append(
                f"mcp '{folder.name}': placeholders {missing} used in config_template but not declared in required_env"
            )


def main() -> int:
    skill_schema = load_json(SCHEMA_DIR / "skill-manifest.schema.json")
    mcp_schema = load_json(SCHEMA_DIR / "mcp-manifest.schema.json")

    errors: list[str] = []

    if SKILLS_DIR.exists():
        for sub in sorted(SKILLS_DIR.iterdir()):
            if sub.is_dir() and not sub.name.startswith("."):
                validate_folder(sub, skill_schema, "skill", errors)

    if MCPS_DIR.exists():
        for sub in sorted(MCPS_DIR.iterdir()):
            if sub.is_dir() and not sub.name.startswith("."):
                validate_folder(sub, mcp_schema, "mcp", errors)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("All manifests valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
