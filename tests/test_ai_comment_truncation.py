"""Test AI comment truncation functionality in sensor.py."""
from pathlib import Path


SENSOR_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "sensor.py"


def test_ai_comment_sensor_truncates_long_comments():
    """Test that CleanMeAICommentSensor has truncation logic for 250 chars."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    # Find the CleanMeAICommentSensor class
    assert "class CleanMeAICommentSensor" in source
    
    # Extract the section for the AI comment sensor
    sensor_section_start = source.find("class CleanMeAICommentSensor")
    sensor_section_end = source.find("class CleanMeMessinessScoreSensor")
    sensor_section = source[sensor_section_start:sensor_section_end]
    
    # Check for truncation logic in native_value
    assert "250" in sensor_section, (
        "CleanMeAICommentSensor should truncate to 250 chars"
    )
    assert "247" in sensor_section, (
        "CleanMeAICommentSensor should leave room for '...' (247 + 3 = 250)"
    )
    assert '..."' in sensor_section or "..." in sensor_section, (
        "CleanMeAICommentSensor should add ellipsis for truncated comments"
    )


def test_ai_comment_sensor_has_extra_state_attributes():
    """Test that CleanMeAICommentSensor has extra_state_attributes with full_comment."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    # Find the CleanMeAICommentSensor class
    sensor_section_start = source.find("class CleanMeAICommentSensor")
    sensor_section_end = source.find("class CleanMeMessinessScoreSensor")
    sensor_section = source[sensor_section_start:sensor_section_end]
    
    # Check for extra_state_attributes property
    assert "extra_state_attributes" in sensor_section, (
        "CleanMeAICommentSensor must have extra_state_attributes property"
    )
    
    # Check for full_comment attribute
    assert "full_comment" in sensor_section, (
        "extra_state_attributes must include 'full_comment'"
    )
    
    # Check for comment_length attribute
    assert "comment_length" in sensor_section, (
        "extra_state_attributes must include 'comment_length'"
    )
    
    # Check for truncated attribute
    assert "truncated" in sensor_section, (
        "extra_state_attributes must include 'truncated' boolean"
    )


def test_ai_comment_sensor_returns_full_comment_under_limit():
    """Test that comments under 250 chars are returned in full."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    # Find the CleanMeAICommentSensor class
    sensor_section_start = source.find("class CleanMeAICommentSensor")
    sensor_section_end = source.find("class CleanMeMessinessScoreSensor")
    sensor_section = source[sensor_section_start:sensor_section_end]
    
    # Check for conditional truncation logic
    assert "if len(comment) > 250" in sensor_section, (
        "CleanMeAICommentSensor should only truncate if comment exceeds 250 chars"
    )
