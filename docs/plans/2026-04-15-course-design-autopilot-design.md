# Design Document: Course Design Autopilot Skill

## Overview
The `course-design-autopilot` is an OhMyOpenCode skill designed to automatically parse assignment zip files provided by teachers, understand requirements, establish a tech stack, implement the code, and generate a final academic report. It uses an Interactive Phased Workflow to ensure the AI's understanding aligns with the user's expectations.

## Architecture

### 1. Setup & Extraction Phase
- **Input:** The user provides the absolute path to a course design `.zip`, `.tar.gz`, or `.rar` file.
- **Process:**
  - Decompress the archive into a standard workspace (e.g., `./course_design_workspace`).
  - Scan for document files (`.pdf`, `.doc`, `.docx`, `.txt`, `.md`).
  - Use a bundled Python script or system utilities (`pdftotext`, `pandoc`, or `pdf` skill) to extract all text.
  - Consolidate all extracted requirements into a single `COURSE_REQUIREMENTS.md` file. This prevents context fragmentation and gives the AI a clean starting point.

### 2. Interactive Orchestration Flow

#### Phase 1: Analysis & Confirmation
- The AI reads `COURSE_REQUIREMENTS.md` and synthesizes the core goal, mandatory features, constraints, and a recommended tech stack.
- **Hard Gate:** The AI stops and asks the user: "Is this understanding correct? Should we adjust the tech stack?"
- Execution only proceeds after user confirmation.

#### Phase 2: Code Implementation
- The AI creates a detailed execution plan based on the confirmed tech stack.
- It delegates actual coding tasks to underlying subagents (e.g., `deep` or `unspecified-high` agents via `task()` tools) to maintain a clear context window and execute efficiently.

#### Phase 3: Verification
- The AI attempts to compile or run the generated code to ensure basic correctness.
- Any immediate errors are triaged and fixed.

#### Phase 4: Report Generation
- A final `REPORT.md` is generated following standard academic templates:
  - 1. Introduction
  - 2. Requirement Analysis
  - 3. System Design
  - 4. Core Implementation details
  - 5. Testing & Results
  - 6. Conclusion
- The user can copy this directly into Word to submit.

## Technical Requirements
- A Python script (`parse_docs.py`) will be bundled with the skill to handle `docx` and `pdf` parsing efficiently without relying on unreliable external APIs.
- The `SKILL.md` file will contain strict instructions enforcing the 4-phase Interactive Workflow and the Hard Gate mechanism.

## Success Criteria
- The skill cleanly extracts non-structured data into Markdown.
- The AI successfully pauses before writing any code.
- A functional codebase and an academic report are generated.
