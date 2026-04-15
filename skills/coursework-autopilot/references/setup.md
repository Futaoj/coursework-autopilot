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

## Script-based fallback

When MCP wiring is unavailable, use these local scripts instead:
- `skills/coursework-autopilot/scripts/extract_course_requirements.py`
- `skills/coursework-autopilot/scripts/inspect_course_workspace.py`
- `skills/coursework-autopilot/scripts/init_report_from_template.py`
