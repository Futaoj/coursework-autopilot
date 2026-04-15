# Course Design Autopilot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an OhMyOpenCode skill that automatically parses assignment zip files, extracts requirements, orchestrates the coding phase interactively, and generates a final academic report.

**Architecture:** 
1. A Python utility script (`parse_docs.py`) to handle zip extraction and unstructured document parsing (PDF, DOCX, TXT) into a clean `REQUIREMENTS.md`.
2. A `SKILL.md` file defining the rigid 4-phase Interactive Workflow prompts and orchestrating subagents.

**Tech Stack:** Python (zipfile, pypdf2/pdfplumber, python-docx), OhMyOpenCode Skill System.

---

### Task 1: Document Parsing Script

**Files:**
- Create: `skills/course-design-autopilot/parse_docs.py`
- Create: `skills/course-design-autopilot/requirements.txt`
- Create: `tests/test_parse_docs.py`

**Step 1: Write the failing test**

```python
# tests/test_parse_docs.py
import os
import zipfile
import subprocess

def test_parse_docs_creates_requirements():
    # Setup dummy zip file
    os.makedirs("dummy_course", exist_ok=True)
    with open("dummy_course/req.txt", "w") as f:
        f.write("Build a student management system")
    
    with zipfile.ZipFile("dummy_course.zip", "w") as z:
        z.write("dummy_course/req.txt", "req.txt")
        
    # Run script
    result = subprocess.run(["python", "skills/course-design-autopilot/parse_docs.py", "dummy_course.zip", "workspace"], capture_output=True)
    
    # Check if REQUIREMENTS.md is created
    assert os.path.exists("workspace/COURSE_REQUIREMENTS.md")
    with open("workspace/COURSE_REQUIREMENTS.md", "r") as f:
        content = f.read()
        assert "Build a student management system" in content
        
    # Cleanup
    os.remove("dummy_course.zip")
    os.remove("dummy_course/req.txt")
    os.rmdir("dummy_course")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_parse_docs.py -v`
Expected: FAIL with "No such file or directory: 'skills/course-design-autopilot/parse_docs.py'"

**Step 3: Write minimal implementation**

```python
# skills/course-design-autopilot/parse_docs.py
import sys
import os
import zipfile

def extract_text(file_path):
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    # Placeholder for PDF and DOCX
    return f"[Content of {file_path}]"

def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_docs.py <zip_path> <workspace_dir>")
        sys.exit(1)
        
    zip_path = sys.argv[1]
    workspace = sys.argv[2]
    
    os.makedirs(workspace, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(workspace)
        
    all_text = "# Course Requirements\n\n"
    for root, dirs, files in os.walk(workspace):
        for file in files:
            if file.endswith(('.txt', '.pdf', '.docx', '.doc')):
                file_path = os.path.join(root, file)
                all_text += f"## {file}\n"
                all_text += extract_text(file_path) + "\n\n"
                
    req_path = os.path.join(workspace, "COURSE_REQUIREMENTS.md")
    with open(req_path, 'w', encoding='utf-8') as f:
        f.write(all_text)
        
    print(f"Extraction complete. Requirements saved to {req_path}")

if __name__ == "__main__":
    main()
```

```text
# skills/course-design-autopilot/requirements.txt
PyPDF2
python-docx
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_parse_docs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_parse_docs.py skills/course-design-autopilot/parse_docs.py skills/course-design-autopilot/requirements.txt
git commit -m "feat: add doc extraction script for course design"
```

### Task 2: Create the SKILL.md definition

**Files:**
- Create: `skills/course-design-autopilot/SKILL.md`

**Step 1: Write SKILL.md implementation**

```markdown
# SKILL.md
Base directory for this skill: <skill-dir>

# Course Design Autopilot

## Overview
This skill acts as a highly disciplined orchestrator to help students complete computer science course designs. It extracts requirements from messy zip archives, enforces an interactive analysis step, spawns subagents to implement the code, and generates an academic report.

## Prerequisites
Ensure Python is installed along with the dependencies in `requirements.txt`.

## Workflow Checklist

You MUST complete these steps in order. DO NOT skip any steps.

1. **Extract Requirements**: Ask the user for the path to the teacher's `.zip` file. Run `python parse_docs.py <zip_path> ./course_workspace` to generate `COURSE_REQUIREMENTS.md`.
2. **Analysis & Confirmation (HARD GATE)**: Read `COURSE_REQUIREMENTS.md`. Output a summary containing: 
   - Core Goal
   - Mandatory Features
   - Recommended Tech Stack
   You MUST stop here and ask the user: "Is this understanding correct? Do you want to change the tech stack?" Do not proceed until they say yes.
3. **Implementation**: Use `task(category="deep")` or `task(category="unspecified-high")` subagents in parallel to generate the codebase based on the confirmed tech stack. 
4. **Verification**: Run the code or compile it. Fix obvious errors.
5. **Report Generation**: Write a `REPORT.md` following academic structures (Intro, Requirement Analysis, System Design, Implementation, Testing, Conclusion).
```

**Step 2: Commit**

```bash
git add skills/course-design-autopilot/SKILL.md
git commit -m "feat: add SKILL.md for course-design-autopilot"
```
