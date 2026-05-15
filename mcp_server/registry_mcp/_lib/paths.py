"""Locate Claude Desktop's config and skills directories."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def claude_config_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA environment variable not set")
        return Path(appdata) / "Claude"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "Claude"


def claude_config_file() -> Path:
    return claude_config_dir() / "claude_desktop_config.json"


def claude_skills_dir() -> Path:
    return claude_config_dir() / "skills"


def registry_state_dir() -> Path:
    return claude_config_dir() / "registry"
