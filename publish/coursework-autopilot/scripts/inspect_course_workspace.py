#!/usr/bin/env python3
"""Inspect a coursework workspace for normalized requirement artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from course_design_autopilot.service import CourseDesignService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect a coursework workspace and report whether normalized requirements exist.",
    )
    parser.add_argument("workspace_path", help="Path to the coursework workspace")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = CourseDesignService().inspect_workspace(Path(args.workspace_path))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
