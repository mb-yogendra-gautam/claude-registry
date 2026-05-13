"""Install and uninstall MCP servers — prompts for env vars, patches config safely."""
from __future__ import annotations

import copy

import click
from rich.console import Console

from .. import config, registry, state

console = Console()


def _prompt_env_vars(required_env: list[dict]) -> dict[str, str]:
    """Ask the user for each required env var, hiding input for secrets."""
    answers: dict[str, str] = {}
    for spec in required_env:
        name = spec["name"]
        desc = spec.get("description", "")
        example = spec.get("example")
        secret = spec.get("secret", False)
        prompt_text = f"{name}\n  {desc}"
        if example and not secret:
            prompt_text += f"\n  example: {example}"
        value = click.prompt(prompt_text, hide_input=secret, type=str)
        answers[name] = value
    return answers


def _substitute(template: dict, values: dict[str, str]) -> dict:
    """Replace <PLACEHOLDER> tokens in env values and args with provided values."""
    result = copy.deepcopy(template)

    def sub(s: str) -> str:
        if isinstance(s, str) and s.startswith("<") and s.endswith(">"):
            key = s[1:-1]
            if key in values:
                return values[key]
        return s

    if "env" in result:
        result["env"] = {k: sub(v) for k, v in result["env"].items()}
    if "args" in result:
        result["args"] = [sub(a) for a in result["args"]]
    return result


@click.command("install-mcp")
@click.argument("mcp_id")
@click.option("--force", is_flag=True, help="Overwrite existing server with same id")
def install_mcp(mcp_id: str, force: bool) -> None:
    entries = registry.fetch_index()
    entry = registry.find_entry(entries, "mcp", mcp_id)
    if not entry:
        console.print(f"[red]MCP '{mcp_id}' not found.[/]")
        raise click.exceptions.Exit(1)

    manifest = registry.fetch_manifest(entry.path)

    if config.has_mcp_server(mcp_id) and not force:
        console.print(f"[yellow]MCP '{mcp_id}' is already configured. Use --force to replace.[/]")
        raise click.exceptions.Exit(1)

    required_env = manifest.get("required_env", [])
    if required_env:
        console.print(f"[bold]'{manifest['name']}' needs the following configuration:[/]\n")
        values = _prompt_env_vars(required_env)
    else:
        values = {}

    server_config = _substitute(manifest["config_template"], values)
    backup = config.add_mcp_server(mcp_id, server_config)
    state.record("mcp", mcp_id, manifest["version"])

    console.print(f"\n[green]✓ Installed MCP '{mcp_id}' v{manifest['version']}[/]")
    if backup:
        console.print(f"[dim]  Previous config backed up to {backup}[/]")
    console.print("[dim]  Restart Claude Desktop to load the new server.[/]")


@click.command("uninstall-mcp")
@click.argument("mcp_id")
def uninstall_mcp(mcp_id: str) -> None:
    removed, backup = config.remove_mcp_server(mcp_id)
    state.forget("mcp", mcp_id)
    if removed:
        console.print(f"[green]✓ Removed MCP '{mcp_id}' from config[/]")
        if backup:
            console.print(f"[dim]  Previous config backed up to {backup}[/]")
    else:
        console.print(f"[yellow]MCP '{mcp_id}' was not in config[/]")
