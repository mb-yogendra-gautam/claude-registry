"""Track installed skills and MCPs so we can update and uninstall cleanly."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import paths

STATE_FILENAME = "installed.json"


def _state_path():
    return paths.registry_state_dir() / STATE_FILENAME


def load() -> dict:
    p = _state_path()
    if not p.exists():
        return {"skills": {}, "mcps": {}}
    with p.open() as f:
        return json.load(f)


def save(state: dict) -> None:
    p = _state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def record(kind: str, entry_id: str, version: str, extra: dict | None = None) -> None:
    state = load()
    bucket = state.setdefault(f"{kind}s", {})
    bucket[entry_id] = {
        "version": version,
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **(extra or {}),
    }
    save(state)


def forget(kind: str, entry_id: str) -> None:
    state = load()
    bucket = state.setdefault(f"{kind}s", {})
    bucket.pop(entry_id, None)
    save(state)
