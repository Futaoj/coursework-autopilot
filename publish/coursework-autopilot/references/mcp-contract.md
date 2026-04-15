# MCP Contract

Read this file before invoking the coursework MCP tools or when the available entry point is unclear.

## Required tools

### `extract_course_requirements`

Use this tool when the user starts from a raw coursework archive and the materials have not yet been normalized into a workspace.

Inputs:
- `archive_path`: absolute path to the teacher archive
- `workspace_path`: absolute path where extracted materials and generated outputs should live

Expected output fields:
- `workspace_path`
- `requirements_path`
- `language`
- `template_path`
- `source_files`

After calling the tool:
- Read the generated `requirements_path`
- Use `language` and `template_path` as hints, not as the final interpretation of the assignment
- Treat `source_files` as an inventory for cross-checking what was parsed

### `inspect_course_workspace`

Use this tool when the user already has a workspace path and you need to know whether extraction has already happened.

Inputs:
- `workspace_path`: absolute path to the workspace

Expected output fields:
- `workspace_path`
- `requirements_exists`
- `requirements_path`
- `language`
- `template_path`

After calling the tool:
- If `requirements_exists` is true, read `requirements_path`
- If `requirements_exists` is false and the archive is available, fall back to `extract_course_requirements`
- If the workspace looks stale or mismatched with the archive, ask before replacing it

## Entry-point rules

- Start from `extract_course_requirements` for a raw `.zip`
- Start from `inspect_course_workspace` for an existing workspace
- Start by reading `COURSE_REQUIREMENTS.md` directly when the user explicitly provides it

## Safety rules

- Do not overwrite an established workspace without checking whether the user wants reuse or a fresh extraction
- Do not assume missing metadata means missing requirements; read the file contents
- Do not treat the tool output as approval to implement; the explicit user confirmation gate still applies
