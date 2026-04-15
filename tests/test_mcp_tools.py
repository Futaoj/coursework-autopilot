from pathlib import Path

from course_design_autopilot.models import CourseRequirementsResult, WorkspaceInspectionResult
from mcp_server.server import extract_course_requirements_tool, inspect_course_workspace_tool


class FakeService:
    def extract_course_requirements(self, archive_path: Path, workspace_path: Path) -> CourseRequirementsResult:
        return CourseRequirementsResult(
            workspace_path=workspace_path,
            requirements_path=workspace_path / "COURSE_REQUIREMENTS.md",
            language="en",
            template_path=None,
            source_files=["req.txt"],
        )

    def inspect_workspace(self, workspace_path: Path) -> WorkspaceInspectionResult:
        return WorkspaceInspectionResult(
            workspace_path=workspace_path,
            requirements_exists=True,
            requirements_path=workspace_path / "COURSE_REQUIREMENTS.md",
            language="en",
            template_path=None,
        )


def test_extract_tool_returns_serializable_result(tmp_path: Path) -> None:
    result = extract_course_requirements_tool(
        archive_path=str(tmp_path / "course.zip"),
        workspace_path=str(tmp_path / "workspace"),
        service=FakeService(),
    )

    assert result["language"] == "en"
    assert result["requirements_path"].endswith("COURSE_REQUIREMENTS.md")
    assert result["source_files"] == ["req.txt"]
    assert result["template_path"] is None


def test_inspect_tool_returns_workspace_metadata(tmp_path: Path) -> None:
    result = inspect_course_workspace_tool(
        workspace_path=str(tmp_path / "workspace"),
        service=FakeService(),
    )

    assert result["requirements_exists"] is True
    assert result["language"] == "en"
    assert result["template_path"] is None
