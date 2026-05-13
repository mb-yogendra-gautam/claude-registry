"""Safely read, modify, and write claude_desktop_config.json.

Every write follows: read → parse → modify in memory → write to temp file →
atomic rename. A timestamped .bak is kept so users can roll back manually.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from . import paths


def read_config() -> dict:
    cfg_path = paths.claude_config_file()
    if not cfg_path.exists():
        return {}
    with cfg_path.open() as f:
        text = f.read().strip()
    if not text:
        return {}
    return json.loads(text)


def _backup(cfg_path: Path) -> Path:
    backups_dir = paths.registry_state_dir() / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = backups_dir / f"claude_desktop_config.{stamp}.json.bak"
    shutil.copy2(cfg_path, dest)
    return dest


def write_config(new_config: dict) -> Path | None:
    """Write the config atomically. Returns path to the backup, or None if there was no prior file."""
    cfg_path = paths.claude_config_file()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)

    backup_path = _backup(cfg_path) if cfg_path.exists() else None

    tmp_path = cfg_path.with_suffix(cfg_path.suffix + ".tmp")
    with tmp_path.open("w") as f:
        json.dump(new_config, f, indent=2)
        f.write("\n")
    os.replace(tmp_path, cfg_path)  # atomic on POSIX and Windows
    return backup_path


def add_mcp_server(server_id: str, server_config: dict) -> Path | None:
    cfg = read_config()
    cfg.setdefault("mcpServers", {})
    cfg["mcpServers"][server_id] = server_config
    return write_config(cfg)


def remove_mcp_server(server_id: str) -> tuple[bool, Path | None]:
    cfg = read_config()
    servers = cfg.get("mcpServers", {})
    if server_id not in servers:
        return False, None
    del servers[server_id]
    backup = write_config(cfg)
    return True, backup


def has_mcp_server(server_id: str) -> bool:
    return server_id in read_config().get("mcpServers", {})
