#!/usr/bin/env python3
"""Bootstrap installer for Claude Registry MCP server.

Adds the registry MCP to Claude Desktop's config file so users can
browse and install skills/MCPs conversationally.

Usage:
    curl -sL https://raw.githubusercontent.com/mb-yogendra-gautam/claude-registry/main/scripts/bootstrap.py | python3
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


def find_config_dir() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Claude"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            print("ERROR: APPDATA not set", file=sys.stderr)
            sys.exit(1)
        return Path(appdata) / "Claude"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg) if xdg else Path.home() / ".config"
        return base / "Claude"


def check_uv_installed() -> bool:
    try:
        subprocess.run(["uvx", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def install_uv():
    print("Installing uv (required to run MCP servers)...")
    system = platform.system()
    if system == "Windows":
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "ByPass", "-c", "irm https://astral.sh/uv/install.ps1 | iex"],
            check=True,
        )
    else:
        subprocess.run(["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"], check=True)
    print("uv installed successfully.\n")


def main():
    print("=== Claude Registry Bootstrap ===\n")

    # Check uv
    if not check_uv_installed():
        print("uv is not installed (needed to run MCP servers).")
        install_uv()
        if not check_uv_installed():
            print("ERROR: uv installation failed. Please install manually: https://docs.astral.sh/uv/getting-started/installation/")
            sys.exit(1)

    config_dir = find_config_dir()
    config_file = config_dir / "claude_desktop_config.json"

    print(f"Config location: {config_file}")

    # Read existing or start fresh
    if config_file.exists():
        with config_file.open() as f:
            text = f.read().strip()
        cfg = json.loads(text) if text else {}
        print("Found existing config.")
    else:
        config_dir.mkdir(parents=True, exist_ok=True)
        cfg = {}
        print("No existing config — creating new one.")

    # Check if already installed
    servers = cfg.get("mcpServers", {})
    if "registry" in servers:
        print("\nRegistry MCP is already configured! No changes needed.")
        print("Restart Claude Desktop if it's not appearing.")
        return

    # Create backup
    if config_file.exists():
        backup_dir = config_dir / "registry" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"claude_desktop_config.{stamp}.json.bak"
        shutil.copy2(config_file, backup_path)
        print(f"Backup saved: {backup_path}")

    # Add registry MCP
    registry_entry = {
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

    cfg.setdefault("mcpServers", {})
    cfg["mcpServers"]["registry"] = registry_entry

    # Atomic write
    tmp_path = config_file.with_suffix(".json.tmp")
    with tmp_path.open("w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    os.replace(tmp_path, config_file)

    print("\nDone! Registry MCP has been added to your Claude Desktop config.")
    print("\nNext steps:")
    print("  1. Restart Claude Desktop (Cmd+Q then reopen)")
    print("  2. Ask Claude: \"What skills and MCPs are available?\"")
    print("\nThe registry MCP will let you browse and install tools conversationally.")


if __name__ == "__main__":
    main()
