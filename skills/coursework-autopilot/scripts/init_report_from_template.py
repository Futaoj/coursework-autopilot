#!/usr/bin/env python3
"""Materialize the bundled coursework report template with simple placeholders."""

from __future__ import annotations

import argparse
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_DIR / "assets" / "report-template" / "REPORT.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a report draft from the bundled coursework template.",
    )
    parser.add_argument("output_path", help="Path to the report file to create")
    parser.add_argument("--title", default="课程设计报告", help="Report title")
    parser.add_argument("--course-name", default="课程名称", help="Course name")
    parser.add_argument("--student-name", default="学生姓名", help="Student name")
    parser.add_argument("--student-id", default="学号", help="Student ID")
    parser.add_argument("--date", default="日期", help="Report date")
    parser.add_argument("--force", action="store_true", help="Overwrite the output if it exists")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_path = Path(args.output_path)

    if output_path.exists() and not args.force:
        raise SystemExit(f"Output already exists: {output_path}. Use --force to overwrite it.")

    content = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": args.title,
        "{{COURSE_NAME}}": args.course_name,
        "{{STUDENT_NAME}}": args.student_name,
        "{{STUDENT_ID}}": args.student_id,
        "{{DATE}}": args.date,
    }
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
