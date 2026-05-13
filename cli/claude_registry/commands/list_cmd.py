"""List and search the catalog."""
from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from .. import registry, state

console = Console()


@click.command("list")
@click.option("--kind", type=click.Choice(["all", "skill", "mcp"]), default="all")
def list_cmd(kind: str) -> None:
    """List everything available in the registry."""
    entries = registry.fetch_index()
    installed = state.load()
    if kind != "all":
        entries = [e for e in entries if e.kind == kind]

    table = Table(title=f"Claude Registry ({len(entries)} items)")
    table.add_column("Kind", style="cyan", width=6)
    table.add_column("ID", style="bold")
    table.add_column("Version", style="dim", width=10)
    table.add_column("Description")
    table.add_column("Status", style="green", width=12)

    for e in entries:
        bucket = installed.get(f"{e.kind}s", {})
        status = ""
        if e.id in bucket:
            inst_v = bucket[e.id]["version"]
            status = "installed" if inst_v == e.version else f"update→{e.version}"
        table.add_row(e.kind, e.id, e.version, e.description[:60], status)
    console.print(table)


@click.command("search")
@click.argument("query")
def search_cmd(query: str) -> None:
    """Search the catalog by name, id, description, or tag."""
    q = query.lower()
    matches = []
    for e in registry.fetch_index():
        haystack = " ".join([e.id, e.name, e.description, " ".join(e.raw.get("tags", []))]).lower()
        if q in haystack:
            matches.append(e)
    if not matches:
        console.print(f"[yellow]No matches for '{query}'[/]")
        return
    table = Table(title=f"Matches for '{query}'")
    table.add_column("Kind", style="cyan")
    table.add_column("ID", style="bold")
    table.add_column("Description")
    for e in matches:
        table.add_row(e.kind, e.id, e.description)
    console.print(table)


@click.command("installed")
def installed_cmd() -> None:
    """Show what you've installed."""
    s = state.load()
    table = Table(title="Installed")
    table.add_column("Kind", style="cyan")
    table.add_column("ID", style="bold")
    table.add_column("Version")
    table.add_column("Installed at", style="dim")
    for kind in ("skill", "mcp"):
        for entry_id, meta in s.get(f"{kind}s", {}).items():
            table.add_row(kind, entry_id, meta["version"], meta.get("installed_at", ""))
    console.print(table)
