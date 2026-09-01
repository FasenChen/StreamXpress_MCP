import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    match = re.search(
        r'^version\s*=\s*"([^"]+)"$', (ROOT / "pyproject.toml").read_text(), re.MULTILINE
    )
    assert match is not None, "pyproject.toml must declare project.version"
    return match.group(1)


def test_readme_declares_project_version():
    version = _project_version()
    assert f"**当前版本：** `{version}`" in (ROOT / "README.md").read_text()


def test_changelog_tracks_project_version():
    version = _project_version()
    changelog = (ROOT / "CHANGELOG.md").read_text()
    assert f"## [{version}]" in changelog
