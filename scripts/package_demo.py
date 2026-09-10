"""Create a portable source archive without virtualenvs, caches or credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
FILES = ["app.py", "README.md", "DEMO.md", "requirements.txt", "pytest.ini", ".gitignore", "TB_AI_Team_External_Candidate_Take_Home_Assignment.pdf"]
DIRECTORIES = [".streamlit", "config", "data", "docs", "src", "tests", "scripts"]


def package() -> Path:
    destination = ROOT / "output/DealSignal-Radar.zip"
    destination.parent.mkdir(exist_ok=True)
    files = [ROOT / name for name in FILES]
    for directory in DIRECTORIES:
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.name != "secrets.toml")
    files.extend((ROOT / "output/playwright").glob("*.png"))
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT))
    with ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Archive integrity check failed")
    return destination


if __name__ == "__main__":
    print(package())
