# Contributing

## Adding a skill

1. Create `skills/<your-id>/` (lowercase, hyphens, must match the `id` in your manifest).
2. Add `manifest.json` — see `schema/skill-manifest.schema.json` and the `pdf-summarizer` example.
3. Add `SKILL.md` (or whatever your `entrypoint` points to) with YAML frontmatter:
   ```yaml
   ---
   name: your-skill
   description: When Claude should use this — be specific about triggers.
   ---
   ```
4. If you have helper scripts or resources, list them in `manifest.json`'s `files` array so the installer copies them.
5. Run `python scripts/validate.py` locally before pushing.

### Writing a good description

The `description` field is what makes Claude reach for your skill. Lead with concrete triggers ("Use when the user mentions X, asks about Y, or uploads a Z file") rather than abstract capabilities.

## Adding an MCP

1. Create `mcps/<your-id>/`.
2. Add `manifest.json`. The two essential fields are:
   - `config_template` — what gets merged into `claude_desktop_config.json`. Use `<PLACEHOLDER>` tokens for anything the user provides.
   - `required_env` — describes each placeholder so the installer can prompt for it. Mark secrets with `"secret": true`.
3. Add a `README.md` explaining setup, especially how to obtain any credentials.
4. Run `python scripts/validate.py` locally.

### Placeholder substitution

Anything in `config_template`'s `env` values or `args` array that looks like `<NAME>` gets substituted with the user's answer to the matching `required_env` entry. Use this for tokens, paths, project IDs — any per-user value.

## Versioning

Use semver. Bump the patch version for fixes, minor for additions, major for breaking changes to the manifest or skill behavior.

## What CI checks

- Every manifest validates against its schema.
- Folder name equals `id`.
- Skill entrypoint and listed files exist.
- Every `<PLACEHOLDER>` in an MCP `config_template` is declared in `required_env`.
- `index.json` matches what `build_index.py` would generate.

## Local development

```bash
uv pip install jsonschema pytest requests click rich
python scripts/validate.py
python scripts/build_index.py
uv run pytest tests/
uv pip install -e cli/      # install the CLI in editable mode
claude-registry list
```
