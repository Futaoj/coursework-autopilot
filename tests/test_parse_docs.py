import os
import zipfile
import importlib.util
from unittest.mock import patch, MagicMock
import pytest


def load_parse_docs():
    """Load parse_docs module from the skill directory."""
    spec = importlib.util.spec_from_file_location(
        "parse_docs",
        os.path.join(os.path.dirname(__file__), "..", "skills", "course-design-autopilot", "parse_docs.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


parse_docs = load_parse_docs()


def test_parse_docs_txt_content_in_requirements(tmp_path):
    """Plain text files are read directly without MinerU."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("requirements.txt", "Build a student management system")

    workspace = str(tmp_path / "workspace")
    parse_docs.main([str(zip_path), workspace])

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert "Build a student management system" in content


def test_parse_docs_yaml_front_matter_written(tmp_path):
    """COURSE_REQUIREMENTS.md starts with YAML front matter block."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("req.txt", "Build something")

    workspace = str(tmp_path / "workspace")
    parse_docs.main([str(zip_path), workspace])

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert content.startswith("---\n")
    assert "language:" in content
    assert "template:" in content
    assert content.count("---") >= 2


def test_parse_docs_detects_chinese_language(tmp_path):
    """Chinese text is detected and written as 'zh' in front matter."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("req.txt", "构建一个学生管理系统，包含增删改查功能，使用Java实现。")

    workspace = str(tmp_path / "workspace")
    parse_docs.main([str(zip_path), workspace])

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert "language: zh" in content


def test_parse_docs_detects_english_language(tmp_path):
    """English text is detected and written as 'en' in front matter."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("req.txt", "Build a student management system with CRUD operations using Java.")

    workspace = str(tmp_path / "workspace")
    parse_docs.main([str(zip_path), workspace])

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert "language: en" in content


def test_parse_docs_detects_template_file(tmp_path):
    """A .docx file with '模板' in the name is recorded as template in front matter."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("课程设计模板.docx", b"PK\x03\x04")  # fake docx magic bytes
        z.writestr("req.txt", "Build something")

    workspace = str(tmp_path / "workspace")

    # Mock _parse_with_mineru so we don't need MinerU installed for this test
    with patch.object(parse_docs, "_parse_with_mineru", return_value="[parsed content]"):
        parse_docs.main([str(zip_path), workspace])

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert "template:" in content
    assert "模板" in content
    assert "null" not in content.split("---")[1]  # template field is not null


def test_parse_docs_no_template_when_absent(tmp_path):
    """When no template .docx is present, template field is 'null'."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("req.txt", "Build something")

    workspace = str(tmp_path / "workspace")
    parse_docs.main([str(zip_path), workspace])

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert "template: null" in content


def test_parse_docs_calls_mineru_for_pdf(tmp_path):
    """PDF files trigger _parse_with_mineru call."""
    zip_path = tmp_path / "course.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("assignment.pdf", b"%PDF-1.4 fake pdf content")

    workspace = str(tmp_path / "workspace")

    with patch.object(parse_docs, "_parse_with_mineru", return_value="Parsed PDF content") as mock_mineru:
        parse_docs.main([str(zip_path), workspace])

    mock_mineru.assert_called_once()
    call_path = mock_mineru.call_args[0][0]
    assert call_path.endswith("assignment.pdf")

    content = open(os.path.join(workspace, "COURSE_REQUIREMENTS.md")).read()
    assert "Parsed PDF content" in content
