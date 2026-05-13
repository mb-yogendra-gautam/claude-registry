"""claude-registry CLI entrypoint."""
from __future__ import annotations

import click

from . import __version__
from .commands.install_mcp import install_mcp, uninstall_mcp
from .commands.install_skill import install_skill, uninstall_skill
from .commands.list_cmd import installed_cmd, list_cmd, search_cmd


@click.group()
@click.version_option(__version__)
def main() -> None:
    """Install Claude Desktop skills and MCP servers from a curated registry."""


main.add_command(list_cmd)
main.add_command(search_cmd)
main.add_command(installed_cmd)
main.add_command(install_skill, name="install-skill")
main.add_command(uninstall_skill, name="uninstall-skill")
main.add_command(install_mcp, name="install-mcp")
main.add_command(uninstall_mcp, name="uninstall-mcp")


@main.command("install")
@click.argument("kind", type=click.Choice(["skill", "mcp"]))
@click.argument("entry_id")
@click.option("--force", is_flag=True)
@click.pass_context
def install(ctx: click.Context, kind: str, entry_id: str, force: bool) -> None:
    """Shorthand: `install skill <id>` or `install mcp <id>`."""
    if kind == "skill":
        ctx.invoke(install_skill, skill_id=entry_id, force=force)
    else:
        ctx.invoke(install_mcp, mcp_id=entry_id, force=force)


@main.command("uninstall")
@click.argument("kind", type=click.Choice(["skill", "mcp"]))
@click.argument("entry_id")
@click.pass_context
def uninstall(ctx: click.Context, kind: str, entry_id: str) -> None:
    """Shorthand: `uninstall skill <id>` or `uninstall mcp <id>`."""
    if kind == "skill":
        ctx.invoke(uninstall_skill, skill_id=entry_id)
    else:
        ctx.invoke(uninstall_mcp, mcp_id=entry_id)


if __name__ == "__main__":
    main()
