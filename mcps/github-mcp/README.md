# GitHub MCP

Lets Claude query your GitHub: list repos, read issues and PRs, search code.

## Setup

1. Create a Personal Access Token at https://github.com/settings/tokens
2. Give it `repo` scope (and `read:org` if you want org search)
3. The installer will prompt for it during install

## Security

The token grants Claude whatever permissions you grant the token. Use a fine-grained PAT scoped to specific repos for the safest setup.
