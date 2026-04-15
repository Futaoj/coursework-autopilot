---
name: coursework-autopilot
description: Orchestrate coursework and course-design delivery from a teacher archive, extracted requirements file, or prepared workspace. Use when Codex needs to turn a coursework `.zip`, mixed PDF/DOCX/TXT materials, or an existing `COURSE_REQUIREMENTS.md` into confirmed requirements, an explicit approval gate, working code, verification, and a submission-ready academic report.
---

# Coursework Autopilot

Use this skill to drive coursework work from raw materials to deliverables without skipping the analysis gate.

## Choose the correct entry point

- If the user provides a raw archive or a folder of teacher materials, read [references/mcp-contract.md](references/mcp-contract.md) and use the extraction workflow.
- If the user already provides a workspace path, inspect whether `COURSE_REQUIREMENTS.md` already exists before deciding to extract again.
- If the user already provides `COURSE_REQUIREMENTS.md`, read it directly and do not ask for re-extraction unless the source materials are missing or clearly stale.

## Use bundled resources deliberately

- Read [references/repo-layout.md](references/repo-layout.md) when you need to know where the extraction logic, MCP server, and tests live.
- Read [references/setup.md](references/setup.md) when the user needs MCP wiring or a local script-based fallback.
- Read [references/report-writing.md](references/report-writing.md) before drafting the final academic report.
- Use `scripts/extract_course_requirements.py` for deterministic local extraction when shell access is available.
- Use `scripts/inspect_course_workspace.py` to check whether a workspace is already normalized before re-extracting.
- Use `scripts/init_report_from_template.py` together with `assets/report-template/REPORT.md` when the user needs a report skeleton quickly.

## Follow the workflow in order

1. Confirm the input path that should drive the task:
   - `archive_path` for a raw `.zip`
   - `workspace_path` for the generated working folder
   - `requirements_path` for an existing `COURSE_REQUIREMENTS.md`
2. If the archive still needs parsing, call MCP tool `extract_course_requirements` with `archive_path` and `workspace_path`.
3. If a workspace already exists, optionally call MCP tool `inspect_course_workspace` to confirm whether `COURSE_REQUIREMENTS.md`, language metadata, or a detected template are already present.
4. Read `COURSE_REQUIREMENTS.md`.
5. Summarize the assignment in a compact structure:
   - Core goal
   - Mandatory features
   - Constraints, deliverables, and grading signals
   - Recommended implementation direction
   - Known unknowns or ambiguities
6. Stop and ask for explicit user confirmation before planning or coding.
7. Only after approval, continue with planning, implementation, verification, and report writing.

## Enforce the approval gate

- Make the confirmation request explicit and easy to answer.
- Do not hide the approval question inside a long paragraph.
- Do not jump from extracted requirements straight into coding.
- If the user changes the scope or tech stack, restate the updated understanding before implementation.

## Write the report in academic prose

- Prefer substantial paragraphs over bullet-heavy notes for main report sections.
- Explain what was built, why it was built that way, how it behaves, and what the results mean.
- Keep headings required by the template, but write paragraph-first content under them.
- Use lists only for genuinely list-shaped material such as environment details, file inventories, or algorithm names.
- Start from the bundled report template when the archive does not already include a stricter template.

## Keep the skill portable

- Do not assume a specific repository layout.
- Do not refer to "this repository" or any local-only path conventions.
- Treat MCP tools as named capabilities, not as hard-coded implementation files.

## Produce these outputs

- Confirmed understanding of the assignment and implementation direction
- `COURSE_REQUIREMENTS.md` when extraction is needed
- Working code after user approval
- Verification results
- A submission-ready report with detailed academic writing
