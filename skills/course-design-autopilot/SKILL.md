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