"""Locate Claude Desktop's config and skills directories.

These paths are stable as of Claude Desktop in 2026, but verify against the
current app version before shipping a new release — Anthropic has changed these
locations in the past.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def claude_config_dir() -> Path:
    """The directory holding claude_desktop_config.json."""
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Claude"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA environment variable not set")
        return Path(appdata) / "Claude"
    # Linux / other
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "Claude"


def claude_config_file() -> Path:
    return claude_config_dir() / "claude_desktop_config.json"


def claude_skills_dir() -> Path:
    """Where Claude Desktop reads user skills from.

    NOTE: confirm the exact path against the Claude Desktop version your users
    run. This default follows the documented convention.
    """
    return claude_config_dir() / "skills"


def registry_state_dir() -> Path:
    """Where this CLI stores its own state (installed.json, backups)."""
    return claude_config_dir() / "registry"
