"""Test dashboard uses Mushroom cards and reads full AI comment from attributes."""
from pathlib import Path


DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "dashboard.py"


def test_dashboard_uses_mushroom_cards():
    """Test that dashboard uses Mushroom card types."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    
    # Check for Mushroom card types
    assert "custom:mushroom-template-card" in source, (
        "Dashboard should use mushroom-template-card"
    )
    assert "custom:mushroom-chips-card" in source, (
        "Dashboard should use mushroom-chips-card"
    )
    assert "custom:mushroom-title-card" in source, (
        "Dashboard should use mushroom-title-card"
    )


def test_dashboard_uses_mini_graph_card():
    """Test that dashboard uses mini-graph-card for messiness history."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    
    assert "custom:mini-graph-card" in source, (
        "Dashboard should use mini-graph-card for messiness history"
    )
    assert "messiness_score" in source, (
        "Dashboard should display messiness score history"
    )


def test_dashboard_reads_full_comment_from_attribute():
    """Test that dashboard reads full AI comment from extra_state_attributes."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    
    # Check that the AI comment section reads from full_comment attribute
    assert "full_comment" in source, (
        "Dashboard should read full_comment from state attributes"
    )
    assert "state_attr" in source, (
        "Dashboard should use state_attr to read the full comment"
    )


def test_dashboard_has_conditional_alert_section():
    """Test that dashboard has conditional card for zones needing attention."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    
    # Check for conditional card
    assert '"type": "conditional"' in source, (
        "Dashboard should have conditional cards for alerts"
    )
    assert "zones_needing_attention" in source, (
        "Dashboard should reference zones_needing_attention entity"
    )


def test_dashboard_has_color_coded_status():
    """Test that dashboard has color-coded status indicators."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    
    # Check for color-coded icons using Jinja templates
    assert "icon_color" in source, (
        "Dashboard should have icon_color properties for status indicators"
    )
    assert "green" in source and "red" in source, (
        "Dashboard should use green/red colors for status indicators"
    )


def test_get_required_custom_cards_returns_mushroom():
    """Test that get_required_custom_cards returns mushroom and mini-graph-card."""
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    
    # Find the function and check its return value
    assert "mushroom" in source, (
        "get_required_custom_cards should return mushroom"
    )
    assert "mini-graph-card" in source, (
        "get_required_custom_cards should return mini-graph-card"
    )
