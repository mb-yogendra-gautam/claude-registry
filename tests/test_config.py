"""Tests for the highest-risk operations: config substitution and atomic writes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Make the cli package importable when running pytest from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cli"))

from claude_registry import config, paths  # noqa: E402
from claude_registry.commands.install_mcp import _substitute  # noqa: E402


def test_substitute_replaces_env_placeholders():
    template = {
        "command": "npx",
        "args": ["-y", "some-package"],
        "env": {"TOKEN": "<MY_TOKEN>", "OTHER": "literal-value"},
    }
    out = _substitute(template, {"MY_TOKEN": "secret123"})
    assert out["env"]["TOKEN"] == "secret123"
    assert out["env"]["OTHER"] == "literal-value"
    assert out["args"] == ["-y", "some-package"]


def test_substitute_replaces_arg_placeholders():
    template = {"command": "npx", "args": ["-y", "pkg", "<ALLOWED_DIR>"]}
    out = _substitute(template, {"ALLOWED_DIR": "/Users/me/workspace"})
    assert out["args"][-1] == "/Users/me/workspace"


def test_substitute_leaves_unknown_placeholders_alone():
    template = {"command": "x", "env": {"A": "<UNKNOWN>"}}
    out = _substitute(template, {})
    assert out["env"]["A"] == "<UNKNOWN>"


def test_config_atomic_write_and_backup(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "claude_config_dir", lambda: tmp_path)
    cfg_path = tmp_path / "claude_desktop_config.json"
    cfg_path.write_text(json.dumps({"mcpServers": {"existing": {"command": "x"}}}))

    backup = config.add_mcp_server("new", {"command": "y"})

    saved = json.loads(cfg_path.read_text())
    assert "existing" in saved["mcpServers"]
    assert saved["mcpServers"]["new"] == {"command": "y"}
    assert backup is not None and backup.exists()


def test_config_creates_file_if_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "claude_config_dir", lambda: tmp_path)
    backup = config.add_mcp_server("new", {"command": "y"})
    assert backup is None  # nothing to back up
    saved = json.loads((tmp_path / "claude_desktop_config.json").read_text())
    assert saved == {"mcpServers": {"new": {"command": "y"}}}


def test_remove_mcp_server(tmp_path, monkeypatch):
    monkeypatch.setattr(paths, "claude_config_dir", lambda: tmp_path)
    config.add_mcp_server("toremove", {"command": "x"})
    removed, _ = config.remove_mcp_server("toremove")
    assert removed
    assert not config.has_mcp_server("toremove")
