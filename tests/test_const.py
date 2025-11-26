import importlib.util
from pathlib import Path


CONST_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "const.py"


def load_const_module():
    spec = importlib.util.spec_from_file_location("cleanme_const", CONST_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_frequency_mappings_are_consistent():
    const = load_const_module()
    assert set(const.FREQUENCY_OPTIONS) == set(const.FREQUENCY_TO_RUNS)
    assert const.FREQUENCY_MANUAL in const.FREQUENCY_OPTIONS
    assert const.FREQUENCY_4X in const.FREQUENCY_TO_RUNS


def test_service_and_attribute_names_are_non_empty():
    const = load_const_module()
    service_names = [
        const.SERVICE_REQUEST_CHECK,
        const.SERVICE_SNOOZE_ZONE,
        const.SERVICE_CLEAR_TASKS,
        const.SERVICE_ADD_ZONE,
        const.SERVICE_MARK_CLEAN,
        const.SERVICE_UNSNOOZE,
        const.SERVICE_CHECK_ALL,
        const.SERVICE_SET_PRIORITY,
    ]
    attribute_names = [
        const.ATTR_TASKS,
        const.ATTR_COMMENT,
        const.ATTR_FULL_ANALYSIS,
        const.ATTR_PERSONALITY,
        const.ATTR_PICKINESS,
        const.ATTR_CAMERA_ENTITY,
        const.ATTR_LAST_CLEANED,
        const.ATTR_CLEAN_STREAK,
        const.ATTR_TOTAL_CLEANS,
        const.ATTR_MESSINESS_SCORE,
    ]

    assert all(service_names), "All service names should be defined"
    assert all(attribute_names), "All attribute names should be defined"


def test_personality_options_cover_personalities():
    const = load_const_module()
    for personality in [
        const.PERSONALITY_CHILL,
        const.PERSONALITY_THOROUGH,
        const.PERSONALITY_STRICT,
        const.PERSONALITY_SARCASTIC,
        const.PERSONALITY_PROFESSIONAL,
    ]:
        assert personality in const.PERSONALITY_OPTIONS


def test_priority_options_defined():
    const = load_const_module()
    assert const.PRIORITY_LOW in const.PRIORITY_OPTIONS
    assert const.PRIORITY_MEDIUM in const.PRIORITY_OPTIONS
    assert const.PRIORITY_HIGH in const.PRIORITY_OPTIONS


def test_platforms_include_all_entity_types():
    const = load_const_module()
    expected_platforms = ["sensor", "binary_sensor", "button", "number", "select"]
    for platform in expected_platforms:
        assert platform in const.PLATFORMS, f"Platform '{platform}' should be in PLATFORMS"
