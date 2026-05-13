"""Fetch the catalog and individual files from the GitHub registry."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests

# Override via env var for testing or self-hosting a fork.
DEFAULT_REGISTRY = "https://raw.githubusercontent.com/YOUR-ORG/claude-registry/main"


def base_url() -> str:
    return os.environ.get("CLAUDE_REGISTRY_URL", DEFAULT_REGISTRY).rstrip("/")


@dataclass
class CatalogEntry:
    kind: str  # "skill" or "mcp"
    id: str
    name: str
    version: str
    description: str
    path: str
    raw: dict


def fetch_index() -> list[CatalogEntry]:
    url = f"{base_url()}/index.json"
    resp = requests.get(url, timeout=15)
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
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_file(path: str, rel: str) -> bytes:
    url = f"{base_url()}/{path}/{rel}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def find_entry(entries: list[CatalogEntry], kind: str, entry_id: str) -> CatalogEntry | None:
    for e in entries:
        if e.kind == kind and e.id == entry_id:
            return e
    return None
