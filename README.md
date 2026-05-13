# Claude Registry

A curated catalog of skills and MCP servers for Claude Desktop, with a CLI installer.

## Getting started

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install the CLI

```bash
uv tool install ./cli
```

### 3. Browse available skills and MCPs

```bash
claude-registry list
```

### 4. Install a skill or MCP

```bash
claude-registry install skill pdf-summarizer
claude-registry install mcp github-mcp
```

### 5. Check what's installed

```bash
claude-registry installed
```

### 6. Restart Claude Desktop

Restart Claude Desktop to pick up newly installed skills and MCPs.

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
export CLAUDE_REGISTRY_URL=https://raw.githubusercontent.com/YOU/your-fork/main
claude-registry list
```
