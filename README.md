# Claude Registry

A curated catalog of skills and MCP servers for Claude Desktop, with a CLI installer.

## Getting started

### Quick Start (Bootstrap Installer)

Run the bootstrap script to add the Registry MCP server to Claude Desktop:

```bash
curl -sL https://raw.githubusercontent.com/mb-yogendra-gautam/claude-registry/main/scripts/bootstrap.py | python3
```

This installs `uv` (if missing) and registers the Registry MCP in your Claude Desktop config. After running it:

1. Restart Claude Desktop.
2. Ask Claude: "What skills and MCPs are available?"
3. Ask Claude to install whichever MCP you want — it handles the rest conversationally.

### CLI Installation (Advanced)

#### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Install the CLI

```bash
uv tool install ./cli
```

#### 3. Install a skill or MCP

```bash
claude-registry install skill pdf-summarizer
claude-registry install mcp github-mcp
```

The CLI will prompt for any required environment variables (API keys, tokens, etc.) and write the config automatically.

#### 4. Restart Claude Desktop

Restart Claude Desktop to pick up newly installed skills and MCPs.

## Useful CLI commands

| Command | Description |
|---------|-------------|
| `claude-registry list` | Browse all available skills and MCPs |
| `claude-registry search <keyword>` | Search the registry |
| `claude-registry installed` | See what's currently installed |
| `claude-registry uninstall mcp <id>` | Remove an installed MCP |

## For contributors

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). Short version:

1. Fork and create a folder under `skills/<your-id>/` or `mcps/<your-id>/`.
2. Add a `manifest.json` matching the schema in `schema/`.
3. Open a PR. CI validates everything.
4. On merge, `index.json` rebuilds automatically.

## Project layout

```
schema/         JSON Schemas every manifest must satisfy
skills/         One folder per skill, named <id>
mcps/           One folder per MCP, named <id>
scripts/        build_index.py, validate.py
cli/            The uv-installable Python CLI
.github/        CI workflows
```

## Self-hosting a fork

Set `CLAUDE_REGISTRY_URL` to your fork's raw URL:

```bash
export CLAUDE_REGISTRY_URL=https://raw.githubusercontent.com/mb-yogendra-gautam/claude-registry/refs/heads/main/index.json
claude-registry list
```
