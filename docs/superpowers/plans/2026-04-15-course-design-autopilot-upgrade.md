# Course Design Autopilot — Pipeline Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing `course-design-autopilot` skill from a stub into a full 3-script pipeline: `parse_docs.py` (MinerU extraction), `generate_diagrams.py` (PlantUML rendering), and `generate_report.py` (PDF generation with template detection).

**Architecture:** Three independent Python scripts are orchestrated by an upgraded `SKILL.md`. `parse_docs.py` extracts documents via MinerU and writes a `COURSE_REQUIREMENTS.md` with YAML front matter (language, template path). `generate_diagrams.py` renders pre-written `.puml` files to PNG using a local PlantUML jar via Java subprocess. `generate_report.py` reads the front matter to choose between filling a detected Word template or generating a `reportlab` PDF, then embeds diagrams and writes `README.md`.

**Tech Stack:** Python 3.10+, `mineru[full]` (magic-pdf), `langdetect`, `python-docx`, `docx2pdf`, `reportlab`, PlantUML JAR + Java ≥ 8, `unittest.mock` for tests.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Modify | `skills/course-design-autopilot/parse_docs.py` | MinerU extraction, language detection, template detection, YAML front matter |
| Modify | `skills/course-design-autopilot/requirements.txt` | Add all new dependencies |
| Create | `skills/course-design-autopilot/generate_diagrams.py` | Render `.puml` → PNG via local Java + PlantUML jar |
| Create | `skills/course-design-autopilot/generate_report.py` | Template-aware PDF generation + README.md |
| Modify | `skills/course-design-autopilot/SKILL.md` | 7-step workflow with hard constraints |
| Modify | `tests/test_parse_docs.py` | Add tests for language detection, template detection, YAML front matter |
| Create | `tests/test_generate_diagrams.py` | Test .puml → PNG dispatch (mock subprocess) |
| Create | `tests/test_generate_report.py` | Test both PDF paths and README.md generation |

---

## Task 1: Upgrade `parse_docs.py` with MinerU, language detection, and template detection

**Files:**
- Modify: `skills/course-design-autopilot/parse_docs.py`
- Modify: `skills/course-design-autopilot/requirements.txt`
- Modify: `tests/test_parse_docs.py`

- [ ] **Step 1: Update requirements.txt**

Replace the entire contents of `skills/course-design-autopilot/requirements.txt` with:

```text
# Document parsing
mineru[full]
langdetect

# Diagram generation
plantuml

# Report generation
python-docx
docx2pdf
reportlab
```

- [ ] **Step 2: Write failing tests for new parse_docs.py behaviour**

Replace the entire contents of `tests/test_parse_docs.py` with:

```python
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
```

- [ ] **Step 3: Run tests to confirm they fail**

```bash
cd /Users/wanghan/Projects/course_work
python -m pytest tests/test_parse_docs.py -v
```

Expected: Most tests FAIL. `test_parse_docs_txt_content_in_requirements` may pass (txt support exists). Others should fail because YAML front matter, language detection, and template detection are not yet implemented.

- [ ] **Step 4: Rewrite parse_docs.py with full implementation**

Replace the entire contents of `skills/course-design-autopilot/parse_docs.py` with:

```python
import sys
import os
import re
import zipfile


# --- MinerU integration ---

def _parse_with_mineru(file_path: str) -> str:
    """Convert a PDF or DOCX file to Markdown using MinerU (magic-pdf).

    MinerU API note: import paths may vary by version. Verify against
    installed version with: python -c "import magic_pdf; help(magic_pdf)"
    """
    from magic_pdf.data.data_reader_writer import FileBasedDataReader
    from magic_pdf.data.dataset import PymuDocDataset
    from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze

    if file_path.endswith((".docx", ".doc")):
        # MinerU's office document support — API may differ by version.
        # Fallback: use python-docx for plain text extraction if this fails.
        try:
            from magic_pdf.tools.office_pipeline import office_convert
            return office_convert(file_path)
        except ImportError:
            from docx import Document
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

    # PDF pipeline
    reader = FileBasedDataReader("")
    pdf_bytes = reader.read(file_path)
    ds = PymuDocDataset(pdf_bytes)
    infer_result = ds.apply(doc_analyze, ocr=False)
    return infer_result.pipe_txt_mode(None, None).get_markdown("")


# --- Language detection ---

def _detect_language(text: str) -> str:
    """Detect primary language of text. Returns 'zh', 'en', or other ISO 639-1 codes.

    Defaults to 'zh' on failure (most common case for this tool's users).
    """
    try:
        from langdetect import detect
        lang = detect(text[:2000])  # use first 2000 chars for speed
        # Normalize Chinese variants (zh-cn, zh-tw → zh)
        return "zh" if lang.startswith("zh") else lang
    except Exception:
        return "zh"


# --- Template detection ---

_TEMPLATE_PATTERN = re.compile(r"(模板|template|格式)", re.IGNORECASE)


def _find_template(workspace: str) -> str | None:
    """Return path to a Word template .docx in workspace, or None."""
    for root, _, files in os.walk(workspace):
        for fname in files:
            if fname.endswith(".docx") and _TEMPLATE_PATTERN.search(fname):
                return os.path.join(root, fname)
    return None


# --- Text extraction ---

def extract_text(file_path: str) -> str:
    """Extract text from a supported file. Calls MinerU for PDF/DOCX."""
    if file_path.endswith(".txt") or file_path.endswith(".md"):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    if file_path.endswith((".pdf", ".docx", ".doc")):
        return _parse_with_mineru(file_path)
    return f"[Unsupported file type: {os.path.basename(file_path)}]"


# --- Main ---

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) < 2:
        print("Usage: python parse_docs.py <zip_path> <workspace_dir>")
        sys.exit(1)

    zip_path, workspace = argv[0], argv[1]
    os.makedirs(workspace, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(workspace)

    # Collect all text from documents
    all_text = ""
    for root, _, files in os.walk(workspace):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            if fname.endswith((".txt", ".md", ".pdf", ".docx", ".doc")):
                all_text += f"\n\n## {fname}\n\n"
                all_text += extract_text(fpath)

    # Detect metadata
    language = _detect_language(all_text)
    template = _find_template(workspace)
    template_val = os.path.relpath(template, workspace) if template else "null"

    # Write COURSE_REQUIREMENTS.md with YAML front matter
    front_matter = f"---\nlanguage: {language}\ntemplate: {template_val}\n---\n\n"
    output = front_matter + "# Course Requirements\n" + all_text

    req_path = os.path.join(workspace, "COURSE_REQUIREMENTS.md")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Extraction complete. Requirements saved to {req_path}")
    print(f"  Language detected: {language}")
    print(f"  Template found: {template_val}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
cd /Users/wanghan/Projects/course_work
python -m pytest tests/test_parse_docs.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/course-design-autopilot/parse_docs.py \
        skills/course-design-autopilot/requirements.txt \
        tests/test_parse_docs.py
git commit -m "feat: upgrade parse_docs.py with MinerU, langdetect, template detection"
```

---

## Task 2: Create `generate_diagrams.py`

**Files:**
- Create: `skills/course-design-autopilot/generate_diagrams.py`
- Create: `tests/test_generate_diagrams.py`

**Context:** This script expects `.puml` files to already exist in `<workspace>/diagrams/` (written by Claude in SKILL.md step 4). It renders each `.puml` to a PNG using a local PlantUML JAR called via Java subprocess. The JAR is downloaded automatically if absent.

- [ ] **Step 1: Write failing tests**

Create `tests/test_generate_diagrams.py`:

```python
import os
import importlib.util
from unittest.mock import patch, call
import pytest


def load_generate_diagrams():
    spec = importlib.util.spec_from_file_location(
        "generate_diagrams",
        os.path.join(
            os.path.dirname(__file__), "..", "skills", "course-design-autopilot", "generate_diagrams.py"
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


generate_diagrams = load_generate_diagrams()


def test_renders_all_puml_files(tmp_path):
    """Each .puml file in workspace/diagrams/ triggers a render call."""
    diagrams_dir = tmp_path / "diagrams"
    diagrams_dir.mkdir()
    (diagrams_dir / "architecture.puml").write_text("@startuml\nA -> B\n@enduml")
    (diagrams_dir / "sequence.puml").write_text("@startuml\nA -> B: hello\n@enduml")

    with patch.object(generate_diagrams, "_render_puml", return_value=None) as mock_render:
        generate_diagrams.main([str(tmp_path)])

    assert mock_render.call_count == 2
    rendered_files = {os.path.basename(c.args[0]) for c in mock_render.call_args_list}
    assert rendered_files == {"architecture.puml", "sequence.puml"}


def test_skips_non_puml_files(tmp_path):
    """Non-.puml files in diagrams/ are ignored."""
    diagrams_dir = tmp_path / "diagrams"
    diagrams_dir.mkdir()
    (diagrams_dir / "note.txt").write_text("ignore me")
    (diagrams_dir / "arch.puml").write_text("@startuml\nA -> B\n@enduml")

    with patch.object(generate_diagrams, "_render_puml", return_value=None) as mock_render:
        generate_diagrams.main([str(tmp_path)])

    assert mock_render.call_count == 1


def test_no_diagrams_dir_exits_cleanly(tmp_path):
    """If workspace/diagrams/ does not exist, script exits with a clear message (no crash)."""
    # Should not raise
    generate_diagrams.main([str(tmp_path)])


def test_render_puml_calls_java_subprocess(tmp_path):
    """_render_puml calls java -jar plantuml.jar for the given file."""
    puml_file = tmp_path / "arch.puml"
    puml_file.write_text("@startuml\nA -> B\n@enduml")
    fake_jar = tmp_path / "plantuml.jar"
    fake_jar.write_bytes(b"fake")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = type("R", (), {"returncode": 0, "stderr": b""})()
        generate_diagrams._render_puml(str(puml_file), str(fake_jar))

    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "java"
    assert "-jar" in cmd
    assert str(fake_jar) in cmd
    assert "-tpng" in cmd
    assert str(puml_file) in cmd


def test_render_puml_raises_on_java_error(tmp_path):
    """_render_puml raises RuntimeError when Java subprocess returns non-zero."""
    puml_file = tmp_path / "arch.puml"
    puml_file.write_text("@startuml\nA -> B\n@enduml")
    fake_jar = tmp_path / "plantuml.jar"
    fake_jar.write_bytes(b"fake")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = type("R", (), {"returncode": 1, "stderr": b"Java error"})()
        with pytest.raises(RuntimeError, match="PlantUML failed"):
            generate_diagrams._render_puml(str(puml_file), str(fake_jar))
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_generate_diagrams.py -v
```

Expected: All 5 tests FAIL with `ModuleNotFoundError` (file doesn't exist yet).

- [ ] **Step 3: Create generate_diagrams.py**

Create `skills/course-design-autopilot/generate_diagrams.py`:

```python
"""generate_diagrams.py — Render PlantUML source files to PNG.

Usage:
    python generate_diagrams.py <workspace_dir>

Expects .puml files in <workspace_dir>/diagrams/.
Outputs .png files alongside each .puml file.

Prerequisites:
    - Java >= 8 on PATH
    - plantuml.jar in the same directory as this script (auto-downloaded if absent)
"""

import sys
import os
import subprocess
import urllib.request

# PlantUML JAR lives next to this script so it's versioned with the skill.
_SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_JAR = os.path.join(_SKILL_DIR, "plantuml.jar")
_PLANTUML_DOWNLOAD_URL = (
    "https://github.com/plantuml/plantuml/releases/download/v1.2024.6/plantuml-1.2024.6.jar"
)


def _ensure_jar(jar_path: str) -> None:
    """Download the PlantUML JAR if it doesn't exist at jar_path."""
    if os.path.exists(jar_path):
        return
    print(f"Downloading PlantUML JAR to {jar_path} ...")
    urllib.request.urlretrieve(_PLANTUML_DOWNLOAD_URL, jar_path)
    print("Download complete.")


def _render_puml(puml_path: str, jar_path: str) -> None:
    """Render a single .puml file to PNG using java -jar plantuml.jar.

    Output PNG is written to the same directory as the .puml file.
    Raises RuntimeError on non-zero Java exit code.
    """
    result = subprocess.run(
        ["java", "-jar", jar_path, "-tpng", puml_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"PlantUML failed for {puml_path}: {result.stderr.decode(errors='replace')}"
        )


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("Usage: python generate_diagrams.py <workspace_dir>")
        sys.exit(1)

    workspace = argv[0]
    diagrams_dir = os.path.join(workspace, "diagrams")

    if not os.path.isdir(diagrams_dir):
        print(f"No diagrams directory found at {diagrams_dir}. Skipping diagram generation.")
        return

    puml_files = [
        os.path.join(diagrams_dir, f)
        for f in sorted(os.listdir(diagrams_dir))
        if f.endswith(".puml")
    ]

    if not puml_files:
        print("No .puml files found in diagrams/. Skipping.")
        return

    _ensure_jar(_DEFAULT_JAR)

    rendered = []
    errors = []
    for puml_path in puml_files:
        try:
            _render_puml(puml_path, _DEFAULT_JAR)
            png_path = puml_path.replace(".puml", ".png")
            rendered.append(png_path)
            print(f"  Rendered: {os.path.basename(png_path)}")
        except RuntimeError as e:
            errors.append(str(e))
            print(f"  ERROR: {e}")

    print(f"\nDiagram generation complete: {len(rendered)} rendered, {len(errors)} errors.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
python -m pytest tests/test_generate_diagrams.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/course-design-autopilot/generate_diagrams.py \
        tests/test_generate_diagrams.py
git commit -m "feat: add generate_diagrams.py with PlantUML JAR rendering"
```

---

## Task 3: Create `generate_report.py`

**Files:**
- Create: `skills/course-design-autopilot/generate_report.py`
- Create: `tests/test_generate_report.py`

**Context:** Reads YAML front matter from `COURSE_REQUIREMENTS.md` to get `language` and `template`. If a `.docx` template is found, fills it with `python-docx` and converts to PDF via `docx2pdf`. Otherwise builds a `reportlab` PDF. Also writes `README.md`.

- [ ] **Step 1: Write failing tests**

Create `tests/test_generate_report.py`:

```python
import os
import importlib.util
from unittest.mock import patch, MagicMock
import pytest


def load_generate_report():
    spec = importlib.util.spec_from_file_location(
        "generate_report",
        os.path.join(
            os.path.dirname(__file__), "..", "skills", "course-design-autopilot", "generate_report.py"
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


generate_report = load_generate_report()


MINIMAL_REQUIREMENTS = """\
---
language: zh
template: null
---

# Course Requirements

## req.txt

构建一个学生管理系统，实现增删改查功能。
"""

REQUIREMENTS_WITH_TEMPLATE = """\
---
language: zh
template: 课程设计模板.docx
---

# Course Requirements

## req.txt

构建一个学生管理系统。
"""


def _write_requirements(workspace: str, content: str) -> None:
    os.makedirs(workspace, exist_ok=True)
    with open(os.path.join(workspace, "COURSE_REQUIREMENTS.md"), "w", encoding="utf-8") as f:
        f.write(content)


def test_read_front_matter_no_template(tmp_path):
    """_read_front_matter returns language='zh' and template=None when template is null."""
    _write_requirements(str(tmp_path), MINIMAL_REQUIREMENTS)
    meta = generate_report._read_front_matter(str(tmp_path))
    assert meta["language"] == "zh"
    assert meta["template"] is None


def test_read_front_matter_with_template(tmp_path):
    """_read_front_matter returns the template path when set."""
    _write_requirements(str(tmp_path), REQUIREMENTS_WITH_TEMPLATE)
    meta = generate_report._read_front_matter(str(tmp_path))
    assert meta["template"] == "课程设计模板.docx"


def test_collect_diagrams_returns_png_paths(tmp_path):
    """_collect_diagrams returns all .png files in workspace/diagrams/."""
    diagrams_dir = tmp_path / "diagrams"
    diagrams_dir.mkdir()
    (diagrams_dir / "architecture.png").write_bytes(b"\x89PNG\r\n")
    (diagrams_dir / "sequence.png").write_bytes(b"\x89PNG\r\n")
    (diagrams_dir / "notes.txt").write_text("ignore")

    pngs = generate_report._collect_diagrams(str(tmp_path))
    assert len(pngs) == 2
    assert all(p.endswith(".png") for p in pngs)


def test_generic_pdf_created_when_no_template(tmp_path):
    """When template is None, _generate_generic_pdf creates REPORT.pdf."""
    _write_requirements(str(tmp_path), MINIMAL_REQUIREMENTS)
    diagrams = []
    meta = {"language": "zh", "template": None}
    body = "系统设计内容"

    with patch.object(generate_report, "_build_reportlab_pdf") as mock_build:
        generate_report._generate_generic_pdf(str(tmp_path), meta, body, diagrams)

    mock_build.assert_called_once()
    out_path = mock_build.call_args[0][0]
    assert out_path.endswith("REPORT.pdf")


def test_template_pdf_created_when_template_present(tmp_path):
    """When template is set, _generate_template_pdf fills docx and converts to PDF."""
    _write_requirements(str(tmp_path), REQUIREMENTS_WITH_TEMPLATE)
    template_path = str(tmp_path / "课程设计模板.docx")
    open(template_path, "wb").write(b"PK\x03\x04")  # fake docx

    meta = {"language": "zh", "template": "课程设计模板.docx"}
    body = "系统设计内容"
    diagrams = []

    with patch("docx.Document") as mock_doc_cls, \
         patch("docx2pdf.convert") as mock_convert:
        mock_doc = MagicMock()
        mock_doc_cls.return_value = mock_doc
        generate_report._generate_template_pdf(str(tmp_path), meta, body, diagrams)

    mock_doc.save.assert_called_once()
    mock_convert.assert_called_once()


def test_readme_written(tmp_path):
    """main() writes README.md to workspace."""
    _write_requirements(str(tmp_path), MINIMAL_REQUIREMENTS)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("def main(): pass")

    with patch.object(generate_report, "_build_reportlab_pdf"), \
         patch.object(generate_report, "_generate_generic_pdf"):
        generate_report.main([str(tmp_path)])

    readme_path = tmp_path / "README.md"
    assert readme_path.exists()
    content = readme_path.read_text()
    assert "main.py" in content


def test_main_dispatches_to_generic_when_no_template(tmp_path):
    """main() calls _generate_generic_pdf when template is null."""
    _write_requirements(str(tmp_path), MINIMAL_REQUIREMENTS)

    with patch.object(generate_report, "_generate_generic_pdf") as mock_generic, \
         patch.object(generate_report, "_generate_template_pdf") as mock_template, \
         patch.object(generate_report, "_write_readme"):
        generate_report.main([str(tmp_path)])

    mock_generic.assert_called_once()
    mock_template.assert_not_called()


def test_main_dispatches_to_template_when_template_present(tmp_path):
    """main() calls _generate_template_pdf when template is set."""
    _write_requirements(str(tmp_path), REQUIREMENTS_WITH_TEMPLATE)
    (tmp_path / "课程设计模板.docx").write_bytes(b"PK\x03\x04")

    with patch.object(generate_report, "_generate_generic_pdf") as mock_generic, \
         patch.object(generate_report, "_generate_template_pdf") as mock_template, \
         patch.object(generate_report, "_write_readme"):
        generate_report.main([str(tmp_path)])

    mock_template.assert_called_once()
    mock_generic.assert_not_called()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_generate_report.py -v
```

Expected: All 8 tests FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Create generate_report.py**

Create `skills/course-design-autopilot/generate_report.py`:

```python
"""generate_report.py — Generate PDF report and README.md from workspace.

Usage:
    python generate_report.py <workspace_dir>

Reads COURSE_REQUIREMENTS.md front matter to determine:
  - language: output language (zh / en)
  - template: path to a .docx school template, or null

If template is set: fills the .docx with python-docx and converts to PDF via docx2pdf.
If template is null: generates a generic reportlab PDF.

Always writes README.md summarising the project structure and key files.
"""

import sys
import os
import re


# --- Front matter parsing ---

def _read_front_matter(workspace: str) -> dict:
    """Parse the YAML front matter block from COURSE_REQUIREMENTS.md.

    Returns dict with keys: 'language' (str), 'template' (str or None).
    """
    req_path = os.path.join(workspace, "COURSE_REQUIREMENTS.md")
    with open(req_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract block between first two '---' lines
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {"language": "zh", "template": None}

    fm_text = match.group(1)
    result = {"language": "zh", "template": None}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if key == "language":
                result["language"] = val
            elif key == "template":
                result["template"] = None if val == "null" else val
    return result


def _read_body(workspace: str) -> str:
    """Read the content section of COURSE_REQUIREMENTS.md (after the front matter)."""
    req_path = os.path.join(workspace, "COURSE_REQUIREMENTS.md")
    with open(req_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Strip YAML front matter
    stripped = re.sub(r"^---\n.*?\n---\n\n?", "", content, flags=re.DOTALL)
    return stripped


# --- Diagram collection ---

def _collect_diagrams(workspace: str) -> list[str]:
    """Return sorted list of PNG paths in workspace/diagrams/."""
    diagrams_dir = os.path.join(workspace, "diagrams")
    if not os.path.isdir(diagrams_dir):
        return []
    return sorted(
        os.path.join(diagrams_dir, f)
        for f in os.listdir(diagrams_dir)
        if f.endswith(".png")
    )


# --- Generic PDF via reportlab ---

def _build_reportlab_pdf(output_path: str, language: str, body: str, diagrams: list[str]) -> None:
    """Build a generic academic PDF using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    # Register CJK font for Chinese support
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    cjk_font = "STSong-Light"

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=2.5*cm, rightMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "CJKBody",
        parent=styles["Normal"],
        fontName=cjk_font,
        fontSize=12,
        leading=20,
        wordWrap="CJK",
    )
    heading_style = ParagraphStyle(
        "CJKHeading",
        parent=styles["Heading1"],
        fontName=cjk_font,
        fontSize=16,
    )

    # Chapter titles by language
    if language == "zh":
        chapters = [
            ("摘要", "本报告描述了课程设计的需求、设计与实现过程。"),
            ("一、需求分析", body[:800] if len(body) > 800 else body),
            ("二、系统设计", "详见系统架构图。"),
            ("三、核心实现", "以下展示核心代码结构与关键模块说明。"),
            ("四、测试与结果", "系统经测试验证，各功能模块运行正常。"),
            ("五、总结", "本次课程设计达成预期目标，完成了系统的设计与实现。"),
        ]
    else:
        chapters = [
            ("Abstract", "This report describes the requirements, design, and implementation."),
            ("1. Requirements Analysis", body[:800] if len(body) > 800 else body),
            ("2. System Design", "See architecture diagram below."),
            ("3. Core Implementation", "Key modules and their responsibilities are described below."),
            ("4. Testing & Results", "All functional modules have been tested and verified."),
            ("5. Conclusion", "The project successfully achieved its design goals."),
        ]

    story = []
    for i, (title, content) in enumerate(chapters):
        story.append(Paragraph(title, heading_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(content.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 0.5*cm))
        # Embed first diagram after System Design chapter
        if i == 2 and diagrams:
            try:
                img = Image(diagrams[0], width=14*cm, height=8*cm, kind="proportional")
                story.append(img)
                story.append(Spacer(1, 0.5*cm))
            except Exception:
                pass  # Skip if image can't be loaded
        # Embed remaining diagrams after Core Implementation
        if i == 3 and len(diagrams) > 1:
            for diag_path in diagrams[1:]:
                try:
                    img = Image(diag_path, width=14*cm, height=8*cm, kind="proportional")
                    story.append(img)
                    story.append(Spacer(1, 0.3*cm))
                except Exception:
                    pass

    doc.build(story)


def _generate_generic_pdf(workspace: str, meta: dict, body: str, diagrams: list[str]) -> str:
    """Generate REPORT.pdf using reportlab. Returns output path."""
    output_path = os.path.join(workspace, "REPORT.pdf")
    _build_reportlab_pdf(output_path, meta["language"], body, diagrams)
    return output_path


# --- Template-based PDF via python-docx + docx2pdf ---

def _generate_template_pdf(workspace: str, meta: dict, body: str, diagrams: list[str]) -> str:
    """Fill a Word template and convert to PDF. Returns output path."""
    import docx
    import docx2pdf

    template_path = os.path.join(workspace, meta["template"])
    doc = docx.Document(template_path)

    # Append body content as new paragraphs after existing template content
    doc.add_heading("需求内容 / Requirements", level=1)
    for para_text in body.split("\n\n"):
        if para_text.strip():
            doc.add_paragraph(para_text.strip())

    # Insert diagrams as inline pictures
    if diagrams:
        doc.add_heading("设计图 / Diagrams", level=1)
        for diag_path in diagrams:
            try:
                doc.add_picture(diag_path, width=docx.shared.Cm(14))
            except Exception:
                pass

    filled_docx = os.path.join(workspace, "REPORT_filled.docx")
    doc.save(filled_docx)

    output_pdf = os.path.join(workspace, "REPORT.pdf")
    docx2pdf.convert(filled_docx, output_pdf)
    return output_pdf


# --- README.md generation ---

def _collect_src_files(workspace: str) -> list[tuple[str, str]]:
    """Return list of (relative_path, first_function_signature) for src/ files."""
    src_dir = os.path.join(workspace, "src")
    if not os.path.isdir(src_dir):
        return []
    result = []
    for root, _, files in os.walk(src_dir):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, workspace)
            first_def = ""
            if fname.endswith(".py"):
                try:
                    content = open(fpath, encoding="utf-8", errors="replace").read()
                    m = re.search(r"^(def |class )\w+", content, re.MULTILINE)
                    if m:
                        first_def = m.group(0).strip()
                except Exception:
                    pass
            result.append((rel, first_def))
    return result


def _write_readme(workspace: str, meta: dict, diagrams: list[str]) -> str:
    """Write README.md with directory tree, file descriptions, and diagram references."""
    src_files = _collect_src_files(workspace)

    lines = []
    if meta["language"] == "zh":
        lines.append("# 课程设计项目说明\n")
        lines.append("## 目录结构\n")
        lines.append("```")
        lines.append("workspace/")
        lines.append("├── COURSE_REQUIREMENTS.md  # 提取的课程需求")
        lines.append("├── REPORT.pdf              # 课程报告")
        lines.append("├── README.md               # 本文件")
        if diagrams:
            lines.append("├── diagrams/               # 设计图")
            for d in diagrams:
                lines.append(f"│   └── {os.path.basename(d)}")
        if src_files:
            lines.append("└── src/                    # 项目代码")
            for rel, _ in src_files:
                lines.append(f"    └── {rel}")
        lines.append("```\n")

        if src_files:
            lines.append("## 重要代码说明\n")
            for rel, first_def in src_files:
                lines.append(f"### `{rel}`")
                if first_def:
                    lines.append(f"主要入口: `{first_def}`")
                lines.append("")
    else:
        lines.append("# Course Design Project\n")
        lines.append("## Directory Structure\n")
        lines.append("```")
        lines.append("workspace/")
        lines.append("├── COURSE_REQUIREMENTS.md  # Extracted requirements")
        lines.append("├── REPORT.pdf              # Academic report")
        lines.append("├── README.md               # This file")
        if diagrams:
            lines.append("├── diagrams/               # Design diagrams")
            for d in diagrams:
                lines.append(f"│   └── {os.path.basename(d)}")
        if src_files:
            lines.append("└── src/                    # Source code")
            for rel, _ in src_files:
                lines.append(f"    └── {rel}")
        lines.append("```\n")

        if src_files:
            lines.append("## Key Files\n")
            for rel, first_def in src_files:
                lines.append(f"### `{rel}`")
                if first_def:
                    lines.append(f"Entry point: `{first_def}`")
                lines.append("")

    if diagrams:
        section_title = "## 设计图预览" if meta["language"] == "zh" else "## Diagram Preview"
        lines.append(section_title + "\n")
        for d in diagrams:
            rel = os.path.relpath(d, workspace)
            name = os.path.basename(d).replace(".png", "")
            lines.append(f"![{name}]({rel})\n")

    readme_path = os.path.join(workspace, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return readme_path


# --- Main ---

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("Usage: python generate_report.py <workspace_dir>")
        sys.exit(1)

    workspace = argv[0]
    meta = _read_front_matter(workspace)
    body = _read_body(workspace)
    diagrams = _collect_diagrams(workspace)

    print(f"Language: {meta['language']}")
    print(f"Template: {meta['template'] or 'none (using generic)'}")
    print(f"Diagrams found: {len(diagrams)}")

    if meta["template"]:
        template_abs = os.path.join(workspace, meta["template"])
        if os.path.exists(template_abs):
            output = _generate_template_pdf(workspace, meta, body, diagrams)
        else:
            print(f"Warning: template '{meta['template']}' not found. Using generic PDF.")
            output = _generate_generic_pdf(workspace, meta, body, diagrams)
    else:
        output = _generate_generic_pdf(workspace, meta, body, diagrams)

    readme = _write_readme(workspace, meta, diagrams)

    print(f"\nReport generated: {output}")
    print(f"README written:   {readme}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
python -m pytest tests/test_generate_report.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/course-design-autopilot/generate_report.py \
        tests/test_generate_report.py
git commit -m "feat: add generate_report.py with template detection and reportlab fallback"
```

---

## Task 4: Upgrade `SKILL.md` to 7-step workflow

**Files:**
- Modify: `skills/course-design-autopilot/SKILL.md`

- [ ] **Step 1: Replace SKILL.md contents**

Replace the entire contents of `skills/course-design-autopilot/SKILL.md` with:

```markdown
# SKILL.md
Base directory for this skill: <skill-dir>

# Course Design Autopilot

## Overview
This skill is a disciplined orchestrator for Chinese university CS course designs. It extracts
teacher-provided materials, interactively confirms requirements, spawns subagents to write code,
renders design diagrams, and produces a PDF report with embedded figures.

## Prerequisites
Before running, ensure:
- Python >= 3.10
- Java >= 8 on PATH (required for PlantUML diagram rendering)
- Dependencies installed: `pip install -r <skill-dir>/requirements.txt`

## Workflow — 7 Steps (MUST complete in order, NEVER skip any step)

---

### Step 1: Extract Requirements

Ask the user:
> "Please provide the path to your teacher's file (ZIP archive, PDF, or DOCX)."

Once the path is provided, run:
```bash
python <skill-dir>/parse_docs.py "<user_path>" ./workspace
```

This produces `workspace/COURSE_REQUIREMENTS.md` with a YAML front matter block containing
detected language and template path. Read this file before continuing.

---

### Step 2: Analysis & Confirmation (HARD GATE — MANDATORY STOP)

Read `workspace/COURSE_REQUIREMENTS.md` in full. Then output a structured summary:

```
语言 / Language: [detected language from front matter]
模板 / Template: [template path if found, or "未检测到 / Not detected"]

核心目标 / Core Goal:
  [one sentence describing the main deliverable]

必做功能 / Mandatory Features:
  - [feature 1]
  - [feature 2]
  - ...

推荐技术栈 / Recommended Tech Stack:
  - Language: [e.g., Java / Python / C++]
  - Framework: [e.g., Spring Boot / Flask / None]
  - Database: [e.g., MySQL / SQLite / None]
  - Build tool: [e.g., Maven / pip / CMake]
```

Then ask:
> "Is this understanding correct? Do you want to adjust the tech stack before I start coding?"

**DO NOT proceed to Step 3 until the user explicitly confirms. This gate cannot be skipped.**

---

### Step 3: Code Implementation

Based on the confirmed tech stack, create a detailed file plan then use parallel subagents
(`task(category="deep")`) to generate the complete codebase into `workspace/src/`.

After all subagents complete:
- List every generated file with a one-line description
- Confirm the project builds or runs without errors (attempt `compile` or `run` as appropriate)

---

### Step 4: Diagram Generation

**This step MUST run after Step 3 is fully complete** — diagrams must reflect the real code structure.

Based on the system design, write PlantUML source files (`.puml`) into `workspace/diagrams/`.
Generate only the diagram types that are relevant to this project:

- `architecture.puml` — component/deployment diagram (almost always relevant)
- `flowchart.puml` — main process flow (relevant if there is a clear user workflow)
- `er.puml` — entity-relationship diagram (relevant if there is a database)
- `sequence.puml` — sequence diagram (relevant if there are multi-party interactions)
- `usecase.puml` — use case diagram (relevant if the spec lists different user roles)

Each `.puml` file must be valid PlantUML syntax starting with `@startuml` and ending with `@enduml`.

Then run:
```bash
python <skill-dir>/generate_diagrams.py ./workspace
```

Report which diagrams were successfully rendered to PNG.

---

### Step 5: Report Generation

Run:
```bash
python <skill-dir>/generate_report.py ./workspace
```

This produces:
- `workspace/REPORT.pdf` — academic report with embedded diagram figures
- `workspace/README.md` — project structure and key code explanations

Report the paths of both output files.

---

### Step 6: Verification

1. Attempt to run or compile the generated code in `workspace/src/`
2. Fix any obvious import errors, missing files, or compilation failures
3. If the report PDF was generated with the generic template, briefly note the chapter structure

---

### Step 7: Delivery Summary

Output a final delivery checklist:

```
✅ workspace/COURSE_REQUIREMENTS.md — 提取的课程需求
✅ workspace/src/                   — 项目代码
✅ workspace/diagrams/              — 设计图 (N 张)
✅ workspace/REPORT.pdf             — 课程报告（含配图）
✅ workspace/README.md              — 项目说明文档

提交建议 / Submission guide:
- 将 REPORT.pdf 直接提交或打印
- 将 src/ 打包为 zip 作为代码附件提交
- 如老师要求 Word 格式：用 Word 打开 REPORT.pdf 或联系助手生成 .docx 版本
```
```

- [ ] **Step 2: Verify SKILL.md is saved correctly**

```bash
cat skills/course-design-autopilot/SKILL.md | head -20
```

Expected: First line is `# SKILL.md`, second line is `Base directory for this skill: <skill-dir>`.

- [ ] **Step 3: Run full test suite to confirm nothing is broken**

```bash
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/course-design-autopilot/SKILL.md
git commit -m "feat: upgrade SKILL.md to 7-step pipeline workflow with hard gate"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task covering it |
|---|---|
| MinerU as hard Python dependency for PDF/DOCX | Task 1: `_parse_with_mineru()` in parse_docs.py |
| Language detection → output language | Task 1: `_detect_language()`, front matter `language` field |
| Template file auto-detection from ZIP | Task 1: `_find_template()`, front matter `template` field |
| YAML front matter in COURSE_REQUIREMENTS.md | Task 1: `main()` writes `---\nlanguage: ...\ntemplate: ...\n---` |
| PlantUML JAR via local Java subprocess | Task 2: `_render_puml()` calls `java -jar plantuml.jar -tpng` |
| Auto-download JAR if absent | Task 2: `_ensure_jar()` downloads from GitHub releases |
| Template path: fill .docx + docx2pdf | Task 3: `_generate_template_pdf()` |
| Generic path: reportlab PDF | Task 3: `_generate_generic_pdf()` + `_build_reportlab_pdf()` |
| Embedded diagram figures in PDF | Task 3: `_build_reportlab_pdf()` inserts `Image()` objects |
| README.md with directory tree + code analysis | Task 3: `_write_readme()` |
| 7-step SKILL.md with HARD GATE at Step 2 | Task 4: SKILL.md rewrite |
| Step 4 must run after Step 3 | Task 4: SKILL.md "MUST run after Step 3 is fully complete" note |
| CJK font support for Chinese PDF | Task 3: `UnicodeCIDFont("STSong-Light")` in reportlab |
| All tests runnable without real dependencies | All tasks: mocked via `unittest.mock.patch` |

**Placeholder scan:** No TBD, TODO, or "implement later" strings found.

**Type consistency:** `_read_front_matter` returns `dict` with keys `language: str` and `template: str | None`. `_generate_template_pdf` and `_generate_generic_pdf` both accept `(workspace: str, meta: dict, body: str, diagrams: list[str])` — consistent across Task 3 tests and implementation.
