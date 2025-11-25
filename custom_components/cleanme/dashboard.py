"""Auto-generate Lovelace dashboard configuration for CleanMe zones.

This dashboard uses ONLY standard Home Assistant Lovelace cards,
no custom cards required.
"""
from __future__ import annotations

from typing import Any, Dict, List

from homeassistant.core import HomeAssistant

from .const import DOMAIN

# Dashboard constants
DASHBOARD_TITLE = "CleanMe"
DASHBOARD_ICON = "mdi:broom"
DASHBOARD_PATH = "cleanme"
DASHBOARD_BADGES: List[Any] = []


def generate_dashboard_config(hass: HomeAssistant) -> Dict[str, Any]:
    """
    Generate a complete Lovelace dashboard configuration for all CleanMe zones.

    Returns a dashboard configuration dict that can be used to create
    a dashboard in Home Assistant.
    """
    zones_data = hass.data.get(DOMAIN, {})

    # Get all zone names
    zone_names = []
    for zone in zones_data.values():
        if hasattr(zone, 'name'):
            zone_names.append(zone.name)

    # Build cards
    cards = []
    
    # Add header/summary card at the top
    cards.append(_create_summary_card(hass))
    
    # Add a card for each zone
    for zone_name in zone_names:
        zone_card = _create_zone_card(zone_name)
        cards.append(zone_card)

    # Build the complete dashboard configuration
    dashboard_config = {
        "title": DASHBOARD_TITLE,
        "icon": DASHBOARD_ICON,
        "path": DASHBOARD_PATH,
        "badges": DASHBOARD_BADGES,
        "cards": cards,
    }

    return dashboard_config


def _create_summary_card(hass: HomeAssistant) -> Dict[str, Any]:
    """Create a header card showing overall house status."""
    return {
        "type": "grid",
        "square": False,
        "columns": 2,
        "cards": [
            # House Status Card
            {
                "type": "entity",
                "entity": "sensor.cleanme_system_status",
                "name": "House Status",
                "icon": "mdi:home-analytics",
            },
            # Quick Stats Card
            {
                "type": "glance",
                "entities": [
                    {
                        "entity": "sensor.cleanme_system_status",
                        "name": "Zones",
                        "attribute": "zone_count",
                    },
                    {
                        "entity": "sensor.cleanme_system_status",
                        "name": "Tasks",
                        "attribute": "task_total",
                    },
                ],
                "show_name": True,
                "show_icon": False,
                "show_state": True,
            },
        ],
    }


def _create_zone_card(zone_name: str) -> Dict[str, Any]:
    """Create a comprehensive card for a single zone using standard Lovelace cards."""
    # Sanitize zone name for entity IDs
    zone_id = zone_name.lower().replace(" ", "_")

    return {
        "type": "vertical-stack",
        "cards": [
            # Zone header with status
            {
                "type": "entities",
                "title": f"🧹 {zone_name}",
                "show_header_toggle": False,
                "entities": [
                    {
                        "entity": f"binary_sensor.{zone_id}_tidy",
                        "name": "Tidy Status",
                        "icon": "mdi:check-circle",
                    },
                    {
                        "entity": f"sensor.{zone_id}_tasks",
                        "name": "Tasks to Complete",
                        "icon": "mdi:format-list-checkbox",
                    },
                    {
                        "entity": f"sensor.{zone_id}_last_check",
                        "name": "Last Checked",
                        "icon": "mdi:clock-outline",
                    },
                ],
            },
            # Task list (conditional - only shown when tasks > 0)
            {
                "type": "conditional",
                "conditions": [
                    {
                        "entity": f"sensor.{zone_id}_tasks",
                        "state_not": "0",
                    }
                ],
                "card": {
                    "type": "markdown",
                    "content": (
                        f"{{% set tasks = state_attr('sensor.{zone_id}_tasks', 'tasks') %}}\n"
                        "{% if tasks %}\n"
                        "**Tasks to complete:**\n"
                        "{% for task in tasks %}\n"
                        "- {{ task }}\n"
                        "{% endfor %}\n"
                        "{% endif %}"
                    ),
                },
            },
            # Comment section (conditional - only shown when comment exists)
            {
                "type": "conditional",
                "conditions": [
                    {
                        "entity": f"sensor.{zone_id}_tasks",
                        "state_not": "unavailable",
                    }
                ],
                "card": {
                    "type": "markdown",
                    "content": (
                        f"{{% set comment = state_attr('sensor.{zone_id}_tasks', 'comment') %}}\n"
                        "{% if comment %}\n"
                        "**💬 AI Comment:** {{ comment }}\n"
                        "{% endif %}"
                    ),
                },
            },
            # Action buttons
            {
                "type": "horizontal-stack",
                "cards": [
                    {
                        "type": "button",
                        "name": "Check Now",
                        "icon": "mdi:camera-iris",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.request_check",
                            "service_data": {
                                "zone": zone_name,
                            },
                        },
                        "icon_height": "40px",
                    },
                    {
                        "type": "button",
                        "name": "Mark Done",
                        "icon": "mdi:check-bold",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.clear_tasks",
                            "service_data": {
                                "zone": zone_name,
                            },
                        },
                        "icon_height": "40px",
                    },
                    {
                        "type": "button",
                        "name": "Snooze 1h",
                        "icon": "mdi:sleep",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.snooze_zone",
                            "service_data": {
                                "zone": zone_name,
                                "duration_minutes": 60,
                            },
                        },
                        "icon_height": "40px",
                    },
                ],
            },
        ],
    }


def generate_basic_dashboard_config(hass: HomeAssistant) -> Dict[str, Any]:
    """
    Generate a basic dashboard configuration without custom cards.
    
    This is an alias for generate_dashboard_config since we now use
    only standard cards.
    """
    return generate_dashboard_config(hass)


def get_required_custom_cards() -> List[str]:
    """
    Return list of custom cards required for the dashboard.
    
    Returns empty list since we now use only standard cards.
    """
    return []


def create_simple_cards_list(hass: HomeAssistant) -> List[Dict[str, Any]]:
    """
    Create a simple list of cards for all zones.

    This is useful for users who want to add CleanMe cards to their
    existing dashboards rather than using the auto-generated one.
    """
    zones_data = hass.data.get(DOMAIN, {})

    cards = []

    for zone in zones_data.values():
        if hasattr(zone, 'name'):
            card = _create_zone_card(zone.name)
            cards.append(card)

    return cards


def create_basic_entities_card(zone_name: str) -> Dict[str, Any]:
    """
    Create a basic entities card that doesn't require custom cards.
    
    This is now the default card type.
    """
    zone_id = zone_name.lower().replace(" ", "_")
    
    return {
        "type": "entities",
        "title": f"🧹 {zone_name}",
        "entities": [
            {
                "entity": f"binary_sensor.{zone_id}_tidy",
                "name": "Status",
            },
            {
                "entity": f"sensor.{zone_id}_tasks",
                "name": "Task Count",
            },
            {
                "entity": f"sensor.{zone_id}_last_check",
                "name": "Last Check",
            },
            {
                "type": "button",
                "name": "Check Now",
                "action_name": "Check",
                "tap_action": {
                    "action": "call-service",
                    "service": "cleanme.request_check",
                    "service_data": {
                        "zone": zone_name,
                    },
                },
            },
            {
                "type": "button",
                "name": "Mark Done",
                "action_name": "Done",
                "tap_action": {
                    "action": "call-service",
                    "service": "cleanme.clear_tasks",
                    "service_data": {
                        "zone": zone_name,
                    },
                },
            },
        ],
    }

