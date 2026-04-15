# Setup

Read this file when the local MCP server needs to be wired into a client or when you need to explain how the project is run.

## Local Python setup

1. Install dependencies from `pyproject.toml`.
2. Run commands from the repository root so relative imports and example paths resolve correctly.

## MCP client wiring

The sample configuration lives in `mcp_server/client-config.example.json`.

Update the `cwd` value to the local repository root, then configure the client to run:

```json
{
  "mcpServers": {
    "coursework-autopilot": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/local/coursework-autopilot"
    }
  }
}
```

## Codex

If your Codex environment supports project-level MCP configuration, reuse the same `command`, `args`, and repository root shown above.

Skill paths:
- development: `skills/coursework-autopilot`
- publishable package: `publish/coursework-autopilot`

## Claude Code

Claude Code supports project-scoped MCP configuration through `.mcp.json`, which is designed to live at the project root and be checked into version control when needed.

Example `.mcp.json`:

```json
{
  "mcpServers": {
    "coursework-autopilot": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {}
    }
  }
}
```

Equivalent CLI flow:

```bash
claude mcp add coursework-autopilot --scope project -- python -m mcp_server
```

## OpenCode

OpenCode configures MCP servers through the `mcp` field in `opencode.json` or `opencode.jsonc`.

Example:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coursework-autopilot": {
      "type": "local",
      "command": ["python", "-m", "mcp_server"],
      "enabled": true
    }
  }
}
```

Useful commands:

```bash
opencode mcp list
opencode run "Use coursework-autopilot to inspect this coursework workspace"
```

## Script-based fallback

When MCP wiring is unavailable, use these local scripts instead:
- `skills/coursework-autopilot/scripts/extract_course_requirements.py`
- `skills/coursework-autopilot/scripts/inspect_course_workspace.py`
- `skills/coursework-autopilot/scripts/init_report_from_template.py`
