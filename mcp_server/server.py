from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from course_design_autopilot.service import CourseDesignService
except ModuleNotFoundError:  # pragma: no cover - local repo fallback
    ROOT = Path(__file__).resolve().parents[1]
    SRC = ROOT / "src"
    sys.path.insert(0, str(SRC))
    from course_design_autopilot.service import CourseDesignService

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - exercised only when dependency is absent
    FastMCP = None


def extract_course_requirements_tool(
    archive_path: str,
    workspace_path: str,
    service: CourseDesignService | None = None,
) -> dict[str, object]:
    resolved_service = service or CourseDesignService()
    result = resolved_service.extract_course_requirements(
        archive_path=Path(archive_path),
        workspace_path=Path(workspace_path),
    )
    return result.to_dict()


def inspect_course_workspace_tool(
    workspace_path: str,
    service: CourseDesignService | None = None,
) -> dict[str, object]:
    resolved_service = service or CourseDesignService()
    result = resolved_service.inspect_workspace(Path(workspace_path))
    return result.to_dict()


def create_server(service: CourseDesignService | None = None):
    if FastMCP is None:
        raise RuntimeError('Install the "mcp" package to run the MCP server.')

    resolved_service = service or CourseDesignService()
    mcp = FastMCP("coursework-autopilot", json_response=True)

    @mcp.tool()
    def extract_course_requirements(archive_path: str, workspace_path: str) -> dict[str, object]:
        """Extract requirements from a coursework or course-design archive."""
        return extract_course_requirements_tool(
            archive_path=archive_path,
            workspace_path=workspace_path,
            service=resolved_service,
        )

    @mcp.tool()
    def inspect_course_workspace(workspace_path: str) -> dict[str, object]:
        """Inspect a generated coursework workspace and summarize metadata."""
        return inspect_course_workspace_tool(
            workspace_path=workspace_path,
            service=resolved_service,
        )

    return mcp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m mcp_server",
        description="Local MCP server for coursework requirement extraction.",
    )
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio"],
        help="Transport to run. Only stdio is implemented in this local build.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    server = create_server()
    server.run(transport=args.transport)
    return 0
