# Repo Layout

Read this file when you need to know where the reusable pieces of the coursework project live.

## Main locations

- `src/course_design_autopilot/`
  Application layer for archive extraction and workspace inspection.
- `mcp_server/`
  Local MCP server that exposes the app layer as tools.
- `skills/coursework-autopilot/scripts/`
  Deterministic helper entry points for extraction, workspace inspection, and report initialization.
- `skills/coursework-autopilot/assets/report-template/`
  Starter report template that can be copied into a workspace.

## Preferred access path

- Use the MCP tools when the runtime supports them and the user is operating through a client.
- Use the bundled scripts when you have direct shell access and need deterministic local execution.
- Read `src/course_design_autopilot/service.py` only when you need to patch or extend the extraction logic.

## Files worth checking early

- `pyproject.toml` for Python dependencies
- `mcp_server/client-config.example.json` for a sample MCP client configuration
- `tests/` for behavior expectations around extraction and inspection
