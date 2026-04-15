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
