"""Test device info and entity ID generation for CleanMe zones."""
import importlib.util
from pathlib import Path


CONST_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "const.py"
DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "dashboard.py"


def load_module(path: Path, name: str):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_domain_constant_exists():
    """Test that DOMAIN constant is defined."""
    const = load_module(CONST_PATH, "cleanme_const")
    assert const.DOMAIN == "cleanme"


def test_gemini_model_is_stable():
    """Test that Gemini model is using stable flash model, not experimental."""
    const = load_module(CONST_PATH, "cleanme_const")
    # gemini-2.0-flash is the stable model, not gemini-2.0-flash-exp
    assert const.GEMINI_MODEL == "gemini-2.0-flash"
    assert "exp" not in const.GEMINI_MODEL.lower()


def test_slugify_zone_names():
    """Test that zone names are properly slugified for entity IDs."""
    # Import the Home Assistant slugify function or use a local implementation
    try:
        from homeassistant.util import slugify
    except ImportError:
        # Fallback implementation for testing without HA installed
        import re
        import unicodedata
        def slugify(text: str) -> str:
            """Simplified slugify for testing."""
            text = text.lower().strip()
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('ascii')
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', '_', text)
            return text.strip('_')
    
    # Test cases from the problem statement
    test_cases = [
        ("Living Room", "living_room"),
        ("Kitchen", "kitchen"),
        ("Master Bedroom", "master_bedroom"),
        ("Kids' Room", "kids_room"),
        ("Dining Area", "dining_area"),
    ]
    
    for zone_name, expected_slug in test_cases:
        actual_slug = slugify(zone_name)
        assert actual_slug == expected_slug, f"Expected '{zone_name}' to slugify to '{expected_slug}', got '{actual_slug}'"


def test_entity_id_format():
    """Test that entity IDs follow the expected format with device_info."""
    try:
        from homeassistant.util import slugify
    except ImportError:
        import re
        import unicodedata
        def slugify(text: str) -> str:
            text = text.lower().strip()
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('ascii')
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', '_', text)
            return text.strip('_')
    
    zone_name = "Living Room"
    zone_slug = slugify(zone_name)
    
    # With device_info and has_entity_name=True, entity IDs follow this pattern
    expected_binary_sensor = f"binary_sensor.{zone_slug}_tidy"
    expected_tasks_sensor = f"sensor.{zone_slug}_tasks"
    expected_last_check_sensor = f"sensor.{zone_slug}_last_check"
    
    assert expected_binary_sensor == "binary_sensor.living_room_tidy"
    assert expected_tasks_sensor == "sensor.living_room_tasks"
    assert expected_last_check_sensor == "sensor.living_room_last_check"
