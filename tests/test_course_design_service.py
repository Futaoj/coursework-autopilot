import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest
from docx import Document

from course_design_autopilot.service import CourseDesignService


def build_archive(archive_path: Path, files: dict[str, str | bytes]) -> None:
    with zipfile.ZipFile(archive_path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_extract_requirements_writes_front_matter_and_content(tmp_path: Path) -> None:
    archive_path = tmp_path / "course.zip"
    workspace = tmp_path / "workspace"
    build_archive(
        archive_path,
        {
            "req.txt": "Build a student management system",
        },
    )

    result = CourseDesignService().extract_course_requirements(archive_path, workspace)

    requirements_path = workspace / "COURSE_REQUIREMENTS.md"
    assert result.requirements_path == requirements_path
    assert requirements_path.exists()
    content = requirements_path.read_text(encoding="utf-8")
    assert content.startswith("---\n")
    assert "language: en" in content
    assert "template: null" in content
    assert "Build a student management system" in content
    assert result.source_files == ["req.txt"]


def test_extract_requirements_detects_template_file(tmp_path: Path) -> None:
    archive_path = tmp_path / "course.zip"
    workspace = tmp_path / "workspace"
    build_archive(
        archive_path,
        {
            "课程设计模板.docx": b"PK\x03\x04",
            "req.txt": "Build something",
        },
    )

    with patch(
        "course_design_autopilot.service._parse_with_mineru",
        return_value="[parsed template]",
    ):
        result = CourseDesignService().extract_course_requirements(archive_path, workspace)

    assert result.template_path == Path("课程设计模板.docx")
    content = (workspace / "COURSE_REQUIREMENTS.md").read_text(encoding="utf-8")
    assert "template: 课程设计模板.docx" in content


def test_extract_requirements_detects_chinese_language(tmp_path: Path) -> None:
    archive_path = tmp_path / "course.zip"
    workspace = tmp_path / "workspace"
    build_archive(
        archive_path,
        {
            "req.txt": "构建一个学生管理系统，包含增删改查功能，使用Java实现。",
        },
    )

    result = CourseDesignService().extract_course_requirements(archive_path, workspace)

    assert result.language == "zh"


def test_extract_requirements_falls_back_when_mineru_missing_for_docx(tmp_path: Path) -> None:
    archive_path = tmp_path / "course.zip"
    workspace = tmp_path / "workspace"
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    docx_path = source_dir / "guide.docx"
    doc = Document()
    doc.add_paragraph("操作系统课程设计要求：实现进程调度与内存管理。")
    doc.save(docx_path)

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(docx_path, "guide.docx")

    result = CourseDesignService().extract_course_requirements(archive_path, workspace)

    assert result.requirements_path.exists()
    content = result.requirements_path.read_text(encoding="utf-8")
    assert "操作系统课程设计要求" in content


def test_extract_requirements_falls_back_when_mineru_missing_for_pdf(tmp_path: Path) -> None:
    archive_path = tmp_path / "course.zip"
    workspace = tmp_path / "workspace"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("guide.pdf", b"%PDF-1.4 fake pdf content")

    with patch(
        "course_design_autopilot.service._parse_pdf_without_mineru",
        return_value="PDF fallback text",
    ):
        result = CourseDesignService().extract_course_requirements(archive_path, workspace)

    assert result.requirements_path.exists()
    content = result.requirements_path.read_text(encoding="utf-8")
    assert "PDF fallback text" in content


def test_inspect_workspace_reports_generated_requirements(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    requirements_path = workspace / "COURSE_REQUIREMENTS.md"
    requirements_path.write_text(
        "---\nlanguage: en\ntemplate: null\n---\n\n# Course Requirements\n",
        encoding="utf-8",
    )

    result = CourseDesignService().inspect_workspace(workspace)

    assert result.workspace_path == workspace
    assert result.requirements_exists is True
    assert result.requirements_path == requirements_path
    assert result.language == "en"
    assert result.template_path is None
