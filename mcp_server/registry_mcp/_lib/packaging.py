"""Shared packaging utilities for building skill zip archives."""
from __future__ import annotations

import io
import zipfile

from . import registry


def build_skill_zip(entry: registry.CatalogEntry, manifest: dict) -> tuple[bytes, list[str]]:
    files = manifest.get("files", [manifest.get("entrypoint", "SKILL.md")])
    buf = io.BytesIO()
    included = []
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            content = registry.fetch_file(entry.path, rel)
            zf.writestr(f"{entry.id}/{rel}", content)
            included.append(rel)
    return buf.getvalue(), included
