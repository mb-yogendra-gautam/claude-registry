"""Install and uninstall skills."""
from __future__ import annotations

import shutil

import click
from rich.console import Console

from .. import paths, registry, state

console = Console()


def _files_to_install(manifest: dict) -> list[str]:
    """Either the explicit list in manifest['files'], or just the entrypoint."""
    if "files" in manifest:
        return manifest["files"]
    return [manifest.get("entrypoint", "SKILL.md")]


@click.command("install-skill")
@click.argument("skill_id")
@click.option("--force", is_flag=True, help="Overwrite if already installed")
def install_skill(skill_id: str, force: bool) -> None:
    entries = registry.fetch_index()
    entry = registry.find_entry(entries, "skill", skill_id)
    if not entry:
        console.print(f"[red]Skill '{skill_id}' not found.[/]")
        raise click.exceptions.Exit(1)

    manifest = registry.fetch_manifest(entry.path)
    dest = paths.claude_skills_dir() / skill_id
    if dest.exists() and not force:
        console.print(f"[yellow]Already installed at {dest}. Use --force to overwrite.[/]")
        raise click.exceptions.Exit(1)

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    for rel in _files_to_install(manifest):
        content = registry.fetch_file(entry.path, rel)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        console.print(f"  ↓ {rel}")

    state.record("skill", skill_id, manifest["version"], {"dest": str(dest)})
    console.print(f"[green]✓ Installed skill '{skill_id}' v{manifest['version']} at {dest}[/]")
    console.print("[dim]Restart Claude Desktop to pick up the new skill.[/]")


@click.command("uninstall-skill")
@click.argument("skill_id")
def uninstall_skill(skill_id: str) -> None:
    installed = state.load().get("skills", {})
    if skill_id not in installed:
        console.print(f"[yellow]Skill '{skill_id}' is not installed.[/]")
        return
    dest = paths.claude_skills_dir() / skill_id
    if dest.exists():
        shutil.rmtree(dest)
    state.forget("skill", skill_id)
    console.print(f"[green]✓ Uninstalled skill '{skill_id}'[/]")
