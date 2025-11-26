"""Test that global entity IDs are correctly configured for dashboard compatibility."""
import importlib.util
from pathlib import Path


SENSOR_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "sensor.py"
BINARY_SENSOR_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "binary_sensor.py"


def test_global_sensor_base_has_entity_name_false():
    """Test that CleanMeGlobalBaseSensor has _attr_has_entity_name = False.
    
    This is critical because global entities without device_info need
    has_entity_name=False so that HA uses the full name for the entity_id.
    """
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    # Find the CleanMeGlobalBaseSensor class definition and verify has_entity_name is False
    assert "class CleanMeGlobalBaseSensor" in source
    
    # Extract the section between CleanMeGlobalBaseSensor and the next class
    sensor_section_start = source.find("class CleanMeGlobalBaseSensor")
    sensor_section_end = source.find("class CleanMeSystemStatusSensor")
    sensor_section = source[sensor_section_start:sensor_section_end]
    
    assert "_attr_has_entity_name = False" in sensor_section, (
        "CleanMeGlobalBaseSensor must have _attr_has_entity_name = False "
        "to ensure entity_ids like sensor.cleanme_system_status are generated"
    )


def test_global_binary_sensor_base_has_entity_name_false():
    """Test that CleanMeGlobalBinarySensor has _attr_has_entity_name = False.
    
    This is critical because global entities without device_info need
    has_entity_name=False so that HA uses the full name for the entity_id.
    """
    source = BINARY_SENSOR_PATH.read_text(encoding="utf-8")
    
    # Find the CleanMeGlobalBinarySensor class definition and verify has_entity_name is False
    assert "class CleanMeGlobalBinarySensor" in source
    
    # Extract the section between CleanMeGlobalBinarySensor and the next class
    sensor_section_start = source.find("class CleanMeGlobalBinarySensor")
    sensor_section_end = source.find("class CleanMeReadyBinarySensor")
    sensor_section = source[sensor_section_start:sensor_section_end]
    
    assert "_attr_has_entity_name = False" in sensor_section, (
        "CleanMeGlobalBinarySensor must have _attr_has_entity_name = False "
        "to ensure entity_ids like binary_sensor.cleanme_ready are generated"
    )


def test_system_status_sensor_name():
    """Test that CleanMeSystemStatusSensor has correct full name."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    # Extract the CleanMeSystemStatusSensor class section
    start = source.find("class CleanMeSystemStatusSensor")
    end = source.find("class CleanMeTotalZonesSensor")
    section = source[start:end]
    
    assert '_attr_name = "CleanMe System Status"' in section, (
        "CleanMeSystemStatusSensor must have full name 'CleanMe System Status' "
        "to generate entity_id sensor.cleanme_system_status"
    )
    assert '_attr_unique_id = "cleanme_system_status"' in section


def test_total_zones_sensor_name():
    """Test that CleanMeTotalZonesSensor has correct full name."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    start = source.find("class CleanMeTotalZonesSensor")
    end = source.find("class CleanMeZonesNeedingAttentionSensor")
    section = source[start:end]
    
    assert '_attr_name = "CleanMe Total Zones"' in section, (
        "CleanMeTotalZonesSensor must have full name 'CleanMe Total Zones' "
        "to generate entity_id sensor.cleanme_total_zones"
    )
    assert '_attr_unique_id = "cleanme_total_zones"' in section


def test_zones_needing_attention_sensor_name():
    """Test that CleanMeZonesNeedingAttentionSensor has correct full name."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    start = source.find("class CleanMeZonesNeedingAttentionSensor")
    end = source.find("class CleanMeNextScheduledCheckSensor")
    section = source[start:end]
    
    assert '_attr_name = "CleanMe Zones Needing Attention"' in section, (
        "CleanMeZonesNeedingAttentionSensor must have full name 'CleanMe Zones Needing Attention' "
        "to generate entity_id sensor.cleanme_zones_needing_attention"
    )
    assert '_attr_unique_id = "cleanme_zones_needing_attention"' in section


def test_next_scheduled_check_sensor_name():
    """Test that CleanMeNextScheduledCheckSensor has correct full name."""
    source = SENSOR_PATH.read_text(encoding="utf-8")
    
    start = source.find("class CleanMeNextScheduledCheckSensor")
    section = source[start:]
    
    assert '_attr_name = "CleanMe Next Scheduled Check"' in section, (
        "CleanMeNextScheduledCheckSensor must have full name 'CleanMe Next Scheduled Check' "
        "to generate entity_id sensor.cleanme_next_scheduled_check"
    )
    assert '_attr_unique_id = "cleanme_next_scheduled_check"' in section


def test_ready_binary_sensor_name():
    """Test that CleanMeReadyBinarySensor has correct full name."""
    source = BINARY_SENSOR_PATH.read_text(encoding="utf-8")
    
    start = source.find("class CleanMeReadyBinarySensor")
    end = source.find("class CleanMeAllTidyBinarySensor")
    section = source[start:end]
    
    assert '_attr_name = "CleanMe Ready"' in section, (
        "CleanMeReadyBinarySensor must have full name 'CleanMe Ready' "
        "to generate entity_id binary_sensor.cleanme_ready"
    )
    assert '_attr_unique_id = "cleanme_ready"' in section


def test_all_tidy_binary_sensor_name():
    """Test that CleanMeAllTidyBinarySensor has correct full name."""
    source = BINARY_SENSOR_PATH.read_text(encoding="utf-8")
    
    start = source.find("class CleanMeAllTidyBinarySensor")
    section = source[start:]
    
    assert '_attr_name = "CleanMe All Tidy"' in section, (
        "CleanMeAllTidyBinarySensor must have full name 'CleanMe All Tidy' "
        "to generate entity_id binary_sensor.cleanme_all_tidy"
    )
    assert '_attr_unique_id = "cleanme_all_tidy"' in section


def test_dashboard_references_match_entity_ids():
    """Test that the dashboard example references match the expected entity IDs.
    
    The dashboard uses entity IDs like:
    - sensor.cleanme_system_status
    - binary_sensor.cleanme_ready
    
    These should match what the entities generate.
    """
    dashboard_path = Path(__file__).resolve().parent.parent / "examples" / "dashboard-example.yaml"
    dashboard_content = dashboard_path.read_text(encoding="utf-8")
    
    # Verify dashboard references the expected entity IDs
    assert "sensor.cleanme_system_status" in dashboard_content, (
        "Dashboard should reference sensor.cleanme_system_status"
    )
    assert "binary_sensor.cleanme_ready" in dashboard_content, (
        "Dashboard should reference binary_sensor.cleanme_ready"
    )
