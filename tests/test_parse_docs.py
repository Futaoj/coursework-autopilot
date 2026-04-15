import os
import zipfile
import subprocess


def test_parse_docs_creates_requirements():
    # Setup dummy zip file
    os.makedirs("dummy_course", exist_ok=True)
    with open("dummy_course/req.txt", "w") as f:
        f.write("Build a student management system")

    with zipfile.ZipFile("dummy_course.zip", "w") as z:
        z.write("dummy_course/req.txt", "req.txt")

    # Run script
    result = subprocess.run(
        [
            "python3",
            "skills/course-design-autopilot/parse_docs.py",
            "dummy_course.zip",
            "workspace",
        ],
        capture_output=True,
    )

    # Check if REQUIREMENTS.md is created
    assert os.path.exists("workspace/COURSE_REQUIREMENTS.md")
    with open("workspace/COURSE_REQUIREMENTS.md", "r") as f:
        content = f.read()
        assert "Build a student management system" in content

    # Cleanup
    os.remove("dummy_course.zip")
    os.remove("dummy_course/req.txt")
    os.rmdir("dummy_course")
