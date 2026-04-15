# Design Spec: Course Design Autopilot — Upgrade to Pipeline Architecture

**Date:** 2026-04-15  
**Status:** Approved  
**Scope:** Upgrade existing `skills/course-design-autopilot` skill

---

## Overview

Upgrade the existing `course-design-autopilot` skill from a stub implementation to a fully functional pipeline. The skill helps Chinese university CS students complete teacher-assigned course designs by:

1. Parsing teacher-provided ZIP/PDF/DOCX materials using MinerU
2. Generating a full codebase via AI subagents
3. Rendering design diagrams (architecture, ER, sequence, flowchart, use case) via PlantUML
4. Producing a final PDF report with embedded figures, either using a detected school template or a generic academic template
5. Generating a README with directory structure and important code analysis

Language of all outputs follows the source material language (auto-detected).

---

## Architecture & Data Flow

```
teacher.zip / .pdf / .docx
        │
        ▼
[parse_docs.py + MinerU]
        │  Extract all docs → Markdown + metadata
        ▼
COURSE_REQUIREMENTS.md  (includes: language, template path if found)
        │
        ▼  HARD GATE: user confirms understanding + tech stack
        │
        ├──► [Claude subagents] Generate code → workspace/src/
        │
        ├──► [generate_diagrams.py + PlantUML]
        │         Claude writes .puml files → script renders PNGs
        │         └─► workspace/diagrams/
        │
        └──► [generate_report.py]
                  ├─ Template detected? → fill .docx → docx2pdf → REPORT.pdf
                  ├─ No template?       → reportlab generic → REPORT.pdf
                  └─► workspace/REPORT.pdf
                      workspace/README.md
```

### Output Directory Structure

```
workspace/
├── COURSE_REQUIREMENTS.md   # Extracted + consolidated requirements
├── src/                     # Generated codebase
├── diagrams/                # PNG diagrams (architecture, ER, sequence, etc.)
├── README.md                # Dir tree + important code explanations
└── REPORT.pdf               # Final academic report with embedded figures
```

---

## Module Details

### `parse_docs.py` (upgrade existing)

**Inputs:** path to ZIP/PDF/DOCX, workspace directory path

**Behavior:**
- Decompress ZIP; recursively scan for documents
- For `.pdf` / `.docx` / `.doc`: call MinerU Python API (`from mineru import ...`) to convert to Markdown
- For `.txt` / `.md`: read directly
- Detect language of consolidated text using `langdetect`; write to metadata header
- Detect template file: any `.docx` whose filename contains "模板", "template", or "格式" (case-insensitive); record path in metadata header

**Output:** `COURSE_REQUIREMENTS.md` with YAML front matter:
```yaml
---
language: zh   # or: en
template: workspace/some_template.docx   # or: null
---
```
Followed by consolidated Markdown content of all extracted documents.

---

### `generate_diagrams.py` (new)

**Inputs:** workspace directory path

**Behavior:**
- Reads all `.puml` files from `workspace/diagrams/` (written by Claude in SKILL.md step 4)
- For each `.puml`: calls `plantuml` Python package (which shells out to local Java) to render PNG
- Skips diagram types not present in requirements (no forced generation)

**Supported diagram types via PlantUML:**
- Architecture diagram (`@startuml` + component)
- Flowchart (`@startuml` + activity)
- ER diagram (`@startuml` + class)
- Sequence diagram (`@startuml` + sequence)
- Use case diagram (`@startuml` + usecase)

**Output:** PNG files in `workspace/diagrams/`, same base name as `.puml` source

**Prerequisite:** Java ≥ 8 installed locally

---

### `generate_report.py` (new)

**Inputs:** workspace directory path

**Behavior:**
1. Reads YAML front matter from `COURSE_REQUIREMENTS.md` to get `language` and `template`
2. Collects all PNG files from `workspace/diagrams/`
3. Reads code summary from `workspace/src/` (file listing + key functions)

**Template path (school template detected):**
- Open `.docx` template with `python-docx`
- Fill section placeholders with generated content
- Insert PNG figures at appropriate positions
- Convert to PDF using `docx2pdf`

**Generic path (no template):**
- Build PDF using `reportlab` with the following chapter structure (in detected language):
  - Abstract / 摘要
  - 1. Requirements Analysis / 需求分析
  - 2. System Design / 系统设计 (includes architecture diagram)
  - 3. Core Implementation / 核心实现 (code excerpts + flowchart/sequence diagram)
  - 4. Testing & Results / 测试与结果
  - 5. Conclusion / 总结
- Embed PNGs inline at relevant sections

**README.md generation (both paths):**
- Directory tree of `workspace/src/`
- Per-file summary of important functions/classes with brief explanations
- References to diagram PNGs using relative Markdown image links

---

## SKILL.md Workflow (7-step upgrade)

```
Step 1: [INPUT]
  Ask user for path to teacher's file (ZIP / PDF / DOCX).
  Run: python parse_docs.py <path> ./workspace

Step 2: [HARD GATE — MANDATORY STOP]
  Read COURSE_REQUIREMENTS.md. Output summary:
    - Detected language: zh / en
    - Template found: yes (path) / no
    - Core goal
    - Mandatory features list
    - Recommended tech stack
  Ask: "Is this understanding correct? Do you want to adjust the tech stack?"
  DO NOT proceed until user explicitly confirms.

Step 3: [CODE IMPLEMENTATION]
  Use task(category="deep") subagents in parallel to generate codebase into workspace/src/.
  After completion, report the list of generated files.

Step 4: [DIAGRAM GENERATION]
  Based on the confirmed system design, write PlantUML source files (.puml) into workspace/diagrams/.
  Generate only diagram types relevant to the project.
  Run: python generate_diagrams.py ./workspace
  Report which diagrams were generated.

Step 5: [REPORT GENERATION]
  Run: python generate_report.py ./workspace
  Report: path to REPORT.pdf and README.md.

Step 6: [VERIFICATION]
  Attempt to install dependencies and run the generated code.
  Triage and fix obvious errors.

Step 7: [DELIVERY SUMMARY]
  List all output files with paths.
  Advise user on submission (e.g., copy REPORT.pdf, zip src/ for submission).
```

**Hard constraints encoded in SKILL.md:**
- Step 2 HARD GATE cannot be skipped under any circumstance
- Step 4 must run after Step 3 is fully complete (diagrams must reflect real code structure)
- Output language and template selection are driven by `parse_docs.py` metadata — never guess

---

## Dependencies (`requirements.txt`)

```text
# Document parsing
mineru[full]       # PDF/DOCX → Markdown (hard dependency)
langdetect         # Language detection

# Diagram generation
plantuml           # PlantUML Python wrapper (requires local Java ≥ 8)

# Report generation
python-docx        # Fill Word templates
docx2pdf           # Word → PDF (school template path)
reportlab          # Generic PDF generation (no-template path)
```

**Prerequisites (written into SKILL.md):**
- Python ≥ 3.10
- Java ≥ 8 (for PlantUML)
- `pip install -r requirements.txt`

---

## Testing Strategy

Three test files, all external calls mocked with `unittest.mock`:

| Test File | Coverage |
|---|---|
| `tests/test_parse_docs.py` | ZIP extraction, MinerU call (mock), language detection, template detection, metadata header output |
| `tests/test_generate_diagrams.py` | `.puml` files present → PNG render called (mock Java), missing Java gives clear error |
| `tests/test_generate_report.py` | Template path: docx filled + docx2pdf called; no-template path: reportlab PDF created; README.md generated |

All tests runnable without MinerU, Java, or docx2pdf installed (fully mocked).

---

## Files Changed

| Action | Path |
|---|---|
| Upgrade | `skills/course-design-autopilot/parse_docs.py` |
| Upgrade | `skills/course-design-autopilot/SKILL.md` |
| Upgrade | `skills/course-design-autopilot/requirements.txt` |
| New | `skills/course-design-autopilot/generate_diagrams.py` |
| New | `skills/course-design-autopilot/generate_report.py` |
| Upgrade | `tests/test_parse_docs.py` |
| New | `tests/test_generate_diagrams.py` |
| New | `tests/test_generate_report.py` |

---

## Success Criteria

- `parse_docs.py` correctly extracts ZIP contents and produces a `COURSE_REQUIREMENTS.md` with valid YAML front matter (language + template path)
- `generate_diagrams.py` renders all `.puml` files in the diagrams directory to PNG
- `generate_report.py` produces a PDF with at least one embedded diagram figure
- SKILL.md HARD GATE at step 2 demonstrably stops execution and waits for user confirmation
- All three test files pass in a mocked environment without real dependencies
