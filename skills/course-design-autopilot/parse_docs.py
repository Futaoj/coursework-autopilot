import sys
import os
import zipfile


def extract_text(file_path):
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    # Placeholder for PDF and DOCX
    return f"[Content of {file_path}]"


def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_docs.py <zip_path> <workspace_dir>")
        sys.exit(1)

    zip_path = sys.argv[1]
    workspace = sys.argv[2]

    os.makedirs(workspace, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(workspace)

    all_text = "# Course Requirements\n\n"
    for root, dirs, files in os.walk(workspace):
        for file in files:
            if file.endswith((".txt", ".pdf", ".docx", ".doc")):
                file_path = os.path.join(root, file)
                all_text += f"## {file}\n"
                all_text += extract_text(file_path) + "\n\n"

    req_path = os.path.join(workspace, "COURSE_REQUIREMENTS.md")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(all_text)

    print(f"Extraction complete. Requirements saved to {req_path}")


if __name__ == "__main__":
    main()
