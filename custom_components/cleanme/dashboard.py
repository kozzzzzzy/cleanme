"""Auto-generate Lovelace dashboard configuration for CleanMe zones.

NOTE: Dashboard cards use custom:mushroom-template-card which requires:
- Mushroom Cards (HACS: piitaya/lovelace-mushroom)
- Card Mod (HACS: thomasloven/lovelace-card-mod)

These dependencies are documented in README.md and should be installed
separately by users who want to use the dashboard features.
"""
from __future__ import annotations

from typing import Any, Dict, List

from homeassistant.core import HomeAssistant

from .const import DOMAIN

# Dashboard constants
DASHBOARD_TITLE = "🏠 Tidy Tracker"
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
    # Note: hass.data[DOMAIN] contains both CleanMeZone objects and metadata keys
    # (like "dashboard_config", "dashboard_panel_registered"), so we use hasattr
    # to filter for actual zone objects that have a 'name' attribute
    zone_names = []
    for zone in zones_data.values():
        if hasattr(zone, 'name'):
            zone_names.append(zone.name)

    # Build cards for each zone
    cards = []

    for zone_name in zone_names:
        zone_card = _create_zone_card(zone_name)
        cards.append(zone_card)

    # Add "Add Zone" button card at the end
    add_zone_card = _create_add_zone_card()
    cards.append(add_zone_card)

    # Build the complete dashboard configuration
    dashboard_config = {
        "title": DASHBOARD_TITLE,
        "icon": DASHBOARD_ICON,
        "path": DASHBOARD_PATH,
        "badges": DASHBOARD_BADGES,
        "cards": cards,
    }

    return dashboard_config


def _create_zone_card(zone_name: str) -> Dict[str, Any]:
    """Create a card for a single zone."""
    # Sanitize zone name for entity IDs
    zone_id = zone_name.lower().replace(" ", "_")

    return {
        "type": "custom:mushroom-template-card",
        "primary": f"🧹 {zone_name}",
        "secondary": "{{ state_attr('sensor." + zone_id + "_tasks', 'comment') }}",
        "icon": "{% if is_state('binary_sensor." + zone_id + "_tidy', 'on') %}mdi:check-circle{% else %}mdi:alert-circle{% endif %}",
        "icon_color": "{% if is_state('binary_sensor." + zone_id + "_tidy', 'on') %}green{% else %}red{% endif %}",
        "badge_icon": "mdi:format-list-checkbox",
        "badge_color": "{% if states('sensor." + zone_id + "_tasks') | int > 0 %}orange{% else %}green{% endif %}",
        "tap_action": {
            "action": "more-info",
        },
        "hold_action": {
            "action": "none",
        },
        "card_mod": {
            "style": """
                ha-card {
                  border-left: 4px solid {% if is_state('binary_sensor.""" + zone_id + """_tidy', 'on') %}var(--success-color){% else %}var(--error-color){% endif %};
                }
            """
        },
    }


def _create_zone_details_card(zone_name: str) -> Dict[str, Any]:
    """Create a detailed card with tasks and action buttons for a zone."""
    zone_id = zone_name.lower().replace(" ", "_")

    return {
        "type": "vertical-stack",
        "cards": [
            # Status header
            {
                "type": "custom:mushroom-template-card",
                "primary": f"{zone_name}",
                "secondary": "{{ state_attr('sensor." + zone_id + "_tasks', 'comment') or 'No recent check' }}",
                "icon": "{% if is_state('binary_sensor." + zone_id + "_tidy', 'on') %}mdi:check-circle{% else %}mdi:alert-circle{% endif %}",
                "icon_color": "{% if is_state('binary_sensor." + zone_id + "_tidy', 'on') %}green{% else %}red{% endif %}",
                "badge_icon": "{% if states('sensor." + zone_id + "_tasks') | int > 0 %}mdi:format-list-checks{% else %}mdi:check{% endif %}",
                "badge_color": "{% if states('sensor." + zone_id + "_tasks') | int > 0 %}orange{% else %}green{% endif %}",
            },
            # Task list (conditional)
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
                    "content": """
{% set tasks = state_attr('sensor.""" + zone_id + """_tasks', 'tasks') %}
{% if tasks %}
**Tasks to complete:**
{% for task in tasks %}
- {{ task }}
{% endfor %}
{% endif %}
                    """,
                },
            },
            # Metadata
            {
                "type": "entities",
                "entities": [
                    {
                        "entity": f"sensor.{zone_id}_last_check",
                        "name": "Last checked",
                    },
                    {
                        "entity": f"sensor.{zone_id}_tasks",
                        "name": "Task count",
                    },
                ],
                "show_header_toggle": False,
            },
            # Action buttons
            {
                "type": "horizontal-stack",
                "cards": [
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Check",
                        "icon": "mdi:camera",
                        "icon_color": "blue",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.request_check",
                            "service_data": {
                                "zone": zone_name,
                            },
                        },
                        "layout": "vertical",
                    },
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Done",
                        "icon": "mdi:check",
                        "icon_color": "green",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.clear_tasks",
                            "service_data": {
                                "zone": zone_name,
                            },
                        },
                        "layout": "vertical",
                    },
                    {
                        "type": "custom:mushroom-template-card",
                        "primary": "Snooze",
                        "icon": "mdi:sleep",
                        "icon_color": "orange",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.snooze_zone",
                            "service_data": {
                                "zone": zone_name,
                                "duration_minutes": 60,
                            },
                        },
                        "layout": "vertical",
                    },
                ],
            },
        ],
    }


def _create_add_zone_card() -> Dict[str, Any]:
    """Create the 'Add Zone' button card."""
    return {
        "type": "custom:mushroom-template-card",
        "primary": "+ Add Another Zone",
        "secondary": "Configure a new room to track",
        "icon": "mdi:plus-circle",
        "icon_color": "blue",
        "tap_action": {
            "action": "navigate",
            "navigation_path": "/config/integrations/integration/cleanme",
        },
        "card_mod": {
            "style": """
                ha-card {
                  border: 2px dashed var(--primary-color);
                  opacity: 0.8;
                }
            """
        },
    }


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
            card = _create_zone_details_card(zone.name)
            cards.append(card)

    return cards


def get_required_custom_cards() -> List[str]:
    """
    Return list of custom cards required for the dashboard.

    These should be installed via HACS for the dashboard to work properly.
    """
    return [
        "mushroom",  # custom:mushroom-template-card
        "card-mod",  # For styling
    ]


def create_basic_entities_card(zone_name: str) -> Dict[str, Any]:
    """
    Create a basic entities card that doesn't require custom cards.
    
    This is a fallback for users who haven't installed Mushroom cards yet.
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


def generate_basic_dashboard_config(hass: HomeAssistant) -> Dict[str, Any]:
    """
    Generate a basic dashboard configuration without custom cards.
    
    This is a fallback for users who haven't installed Mushroom cards.
    """
    zones_data = hass.data.get(DOMAIN, {})
    
    # Get all zone names
    # Note: hass.data[DOMAIN] contains both CleanMeZone objects and metadata keys,
    # so we use hasattr to filter for actual zone objects
    zone_names = []
    for zone in zones_data.values():
        if hasattr(zone, 'name'):
            zone_names.append(zone.name)
    
    # Build basic cards for each zone
    cards = []
    
    for zone_name in zone_names:
        zone_card = create_basic_entities_card(zone_name)
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
