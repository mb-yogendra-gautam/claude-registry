"""Fetch the catalog and individual files from the GitHub registry."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests

DEFAULT_REGISTRY = "https://raw.githubusercontent.com/mb-yogendra-gautam/claude-registry/main"


def base_url() -> str:
    return os.environ.get("CLAUDE_REGISTRY_URL", DEFAULT_REGISTRY).rstrip("/")


def _headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return {"Authorization": f"token {token}"}
    return {}


@dataclass
class CatalogEntry:
    kind: str
    id: str
    name: str
    version: str
    description: str
    path: str
    raw: dict


def fetch_index() -> list[CatalogEntry]:
    url = f"{base_url()}/index.json"
    resp = requests.get(url, timeout=15, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    entries: list[CatalogEntry] = []
    for s in data.get("skills", []):
        entries.append(CatalogEntry("skill", s["id"], s["name"], s["version"], s["description"], s["path"], s))
    for m in data.get("mcps", []):
        entries.append(CatalogEntry("mcp", m["id"], m["name"], m["version"], m["description"], m["path"], m))
    return entries


def fetch_manifest(path: str) -> dict:
    url = f"{base_url()}/{path}/manifest.json"
    resp = requests.get(url, timeout=15, headers=_headers())
    resp.raise_for_status()
    return resp.json()


def fetch_file(path: str, rel: str) -> bytes:
    url = f"{base_url()}/{path}/{rel}"
    resp = requests.get(url, timeout=30, headers=_headers())
    resp.raise_for_status()
    return resp.content


def find_entry(entries: list[CatalogEntry], kind: str, entry_id: str) -> CatalogEntry | None:
    for e in entries:
        if e.kind == kind and e.id == entry_id:
            return e
    return None
