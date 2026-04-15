from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CourseRequirementsResult:
    workspace_path: Path
    requirements_path: Path
    language: str
    template_path: Path | None
    source_files: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_path": str(self.workspace_path),
            "requirements_path": str(self.requirements_path),
            "language": self.language,
            "template_path": None if self.template_path is None else str(self.template_path),
            "source_files": self.source_files,
        }


@dataclass(frozen=True)
class WorkspaceInspectionResult:
    workspace_path: Path
    requirements_exists: bool
    requirements_path: Path
    language: str | None
    template_path: Path | None

    def to_dict(self) -> dict[str, object]:
        return {
            "workspace_path": str(self.workspace_path),
            "requirements_exists": self.requirements_exists,
            "requirements_path": str(self.requirements_path),
            "language": self.language,
            "template_path": None if self.template_path is None else str(self.template_path),
        }
