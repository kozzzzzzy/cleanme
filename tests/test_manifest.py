import json
from pathlib import Path


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "manifest.json"


def test_manifest_fields_present():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    # Core metadata
    assert manifest.get("domain") == "cleanme"
    assert manifest.get("name"), "Manifest must include a human-readable name"
    assert manifest.get("version"), "Manifest version is required for updates"

    # Basic integration metadata
    assert manifest.get("documentation"), "Documentation URL should be set"
    assert manifest.get("issue_tracker"), "Issue tracker URL should be set"

    # Dependencies and requirements
    requirements = manifest.get("requirements", [])
    assert "aiohttp>=3.8.0" in requirements

    dependencies = manifest.get("dependencies", [])
    assert "frontend" in dependencies

    # Config flow & ownership
    assert manifest.get("config_flow") is True
    assert manifest.get("codeowners"), "Codeowners should not be empty"


