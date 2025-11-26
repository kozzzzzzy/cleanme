"""Auto-generate Lovelace dashboard configuration for CleanMe zones.

This dashboard uses Bubble Card for a modern, beautiful UI.
Falls back to standard Home Assistant cards if Bubble Card is not available.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Dashboard constants
DASHBOARD_TITLE = "CleanMe"
DASHBOARD_ICON = "mdi:broom"
DASHBOARD_PATH = "cleanme"
DASHBOARD_BADGES: List[Any] = []


def generate_dashboard_config(hass: HomeAssistant) -> Dict[str, Any]:
    """
    Generate a complete Lovelace dashboard configuration for all CleanMe zones.
    
    Uses Bubble Card for a modern, beautiful interface.
    
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
    
    # 1. App header with Bubble separator
    cards.append(_create_bubble_separator("CleanMe Dashboard", "mdi:broom"))
    
    # 2. Status overview row (House status + CleanMe health)
    cards.append(_create_status_overview_row(hass))
    
    # 3. "What should I do now?" main CTA card with action buttons
    if zone_names:
        cards.append(_create_main_cta_card(hass, zone_names))
    
    # 4. Zones grid with Bubble button cards
    if zone_names:
        cards.append(_create_bubble_separator("Your Zones", "mdi:home-group"))
        cards.extend(_create_zones_grid(zone_names))
    
    # 5. Quick actions row
    cards.append(_create_bubble_separator("Quick Actions", "mdi:lightning-bolt"))
    cards.append(_create_quick_actions_row())
    
    # 6. System info section for power users
    cards.append(_create_bubble_separator("System Info", "mdi:information"))
    cards.append(_create_system_info_section(hass))

    # Build the complete dashboard configuration
    dashboard_config = {
        "title": DASHBOARD_TITLE,
        "icon": DASHBOARD_ICON,
        "path": DASHBOARD_PATH,
        "badges": DASHBOARD_BADGES,
        "cards": cards,
    }

    return dashboard_config


def _create_bubble_separator(title: str, icon: str) -> Dict[str, Any]:
    """Create a Bubble Card separator/header."""
    return {
        "type": "custom:bubble-card",
        "card_type": "separator",
        "name": title,
        "icon": icon,
        "styles": """
          .bubble-line {
            background: var(--primary-color);
            opacity: 0.5;
          }
        """
    }


def _create_status_overview_row(hass: HomeAssistant) -> Dict[str, Any]:
    """Create status overview with Bubble Cards showing house status and system health."""
    zones_data = hass.data.get(DOMAIN, {})
    zone_count = sum(1 for zone in zones_data.values() if hasattr(zone, 'name'))
    
    return {
        "type": "horizontal-stack",
        "cards": [
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "entity": "sensor.cleanme_system_status",
                "name": "House Status",
                "icon": "mdi:home-analytics",
                "show_state": True,
                "show_last_changed": False,
                "tap_action": {"action": "more-info"},
                "styles": """
                  .bubble-button-card-container {
                    background: var(--card-background-color);
                  }
                """
            },
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "entity": "binary_sensor.cleanme_ready",
                "name": "CleanMe Status",
                "icon": "mdi:robot-vacuum",
                "show_state": True,
                "show_last_changed": False,
                "tap_action": {"action": "more-info"},
                "styles": """
                  .bubble-button-card-container {
                    background: var(--card-background-color);
                  }
                """
            }
        ]
    }


def _create_main_cta_card(hass: HomeAssistant, zone_names: List[str]) -> Dict[str, Any]:
    """Create main call-to-action card with prominent action buttons."""
    zones_data = hass.data.get(DOMAIN, {})
    
    # Count zones that need attention
    messy_zones = []
    for zone in zones_data.values():
        if hasattr(zone, 'name') and hasattr(zone, 'state'):
            if not zone.state.tidy:
                messy_zones.append(zone.name)
    
    if messy_zones:
        cta_text = f"{len(messy_zones)} zone{'s' if len(messy_zones) > 1 else ''} need attention"
        cta_sub = f"Let's tackle: {', '.join(messy_zones[:2])}" if len(messy_zones) <= 2 else f"Let's get started"
    else:
        cta_text = "Looking good"
        cta_sub = "All zones are tidy"
    
    return {
        "type": "custom:bubble-card",
        "card_type": "pop-up",
        "hash": "#cleanme-actions",
        "name": cta_text,
        "icon": "mdi:broom" if messy_zones else "mdi:check-circle",
        "entity": "sensor.cleanme_system_status",
        "show_state": True,
        "sub_button": [
            {
                "name": "Check All",
                "icon": "mdi:camera-iris",
                "tap_action": {
                    "action": "call-service",
                    "service": "script.cleanme_check_all_zones",
                }
            },
            {
                "name": "Dashboard",
                "icon": "mdi:view-dashboard",
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "/cleanme"
                }
            }
        ],
        "styles": """
          .bubble-pop-up-container {
            background: var(--primary-color);
            color: var(--text-primary-color);
          }
          .bubble-name {
            font-size: 1.2em;
            font-weight: bold;
          }
          .bubble-sub-name {
            opacity: 0.8;
          }
        """
    }


def _create_zones_grid(zone_names: List[str]) -> List[Dict[str, Any]]:
    """Create a grid of Bubble button cards for each zone."""
    zone_cards = []
    
    for zone_name in zone_names:
        zone_slug = slugify(zone_name)
        _LOGGER.debug(
            "Creating zone card for '%s' with slug '%s'",
            zone_name,
            zone_slug,
        )
        
        zone_card = {
            "type": "custom:bubble-card",
            "card_type": "button",
            "entity": f"binary_sensor.{zone_slug}_tidy",
            "name": zone_name,
            "icon": "mdi:home",
            "show_state": True,
            "show_attribute": False,
            "show_last_changed": True,
            "tap_action": {"action": "more-info"},
            "sub_button": [
                {
                    "name": "Check",
                    "icon": "mdi:camera-iris",
                    "show_background": False,
                    "tap_action": {
                        "action": "call-service",
                        "service": "cleanme.request_check",
                        "service_data": {
                            "zone": zone_name
                        }
                    }
                },
                {
                    "name": "Done",
                    "icon": "mdi:check-bold",
                    "show_background": False,
                    "tap_action": {
                        "action": "call-service",
                        "service": "cleanme.clear_tasks",
                        "service_data": {
                            "zone": zone_name
                        }
                    }
                },
                {
                    "name": "Snooze",
                    "icon": "mdi:sleep",
                    "show_background": False,
                    "tap_action": {
                        "action": "call-service",
                        "service": "cleanme.snooze_zone",
                        "service_data": {
                            "zone": zone_name,
                            "duration_minutes": 60
                        }
                    }
                }
            ],
            "styles": """
              .bubble-button-card-container {
                background: linear-gradient(135deg, var(--card-background-color) 0%, var(--secondary-background-color) 100%);
                border: 2px solid var(--primary-color);
                border-radius: 16px;
                transition: all 0.3s ease;
              }
              .bubble-button-card-container:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
              }
              .bubble-icon {
                color: var(--primary-color);
              }
            """
        }
        
        zone_cards.append(zone_card)
    
    # Wrap in grid layout
    if len(zone_cards) > 1:
        return [{
            "type": "grid",
            "square": False,
            "columns": 2,
            "cards": zone_cards
        }]
    else:
        return zone_cards


def _create_quick_actions_row() -> Dict[str, Any]:
    """Create a row of quick action Bubble buttons."""
    return {
        "type": "horizontal-stack",
        "cards": [
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "name": "Add Zone",
                "icon": "mdi:plus-circle",
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "/config/integrations/integration/cleanme"
                },
                "button_type": "name",
                "styles": """
                  .bubble-button-card-container {
                    background: var(--primary-color);
                    color: var(--text-primary-color);
                  }
                """
            },
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "name": "Settings",
                "icon": "mdi:cog",
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "/config/integrations/integration/cleanme"
                },
                "button_type": "name",
                "styles": """
                  .bubble-button-card-container {
                    background: var(--secondary-background-color);
                  }
                """
            },
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "name": "Reload",
                "icon": "mdi:refresh",
                "tap_action": {
                    "action": "call-service",
                    "service": "cleanme.regenerate_dashboard"
                },
                "button_type": "name",
                "styles": """
                  .bubble-button-card-container {
                    background: var(--secondary-background-color);
                  }
                """
            }
        ]
    }


def _create_system_info_section(hass: HomeAssistant) -> Dict[str, Any]:
    """Create system information section for power users."""
    return {
        "type": "entities",
        "title": "System Details",
        "show_header_toggle": False,
        "entities": [
            {
                "entity": "binary_sensor.cleanme_ready",
                "name": "System Ready",
                "icon": "mdi:check-circle"
            },
            {
                "entity": "sensor.cleanme_system_status",
                "type": "attribute",
                "attribute": "zone_count",
                "name": "Total Zones",
                "icon": "mdi:counter"
            },
            {
                "entity": "sensor.cleanme_system_status",
                "type": "attribute",
                "attribute": "task_total",
                "name": "Total Tasks",
                "icon": "mdi:format-list-checkbox"
            },
            {
                "entity": "binary_sensor.cleanme_ready",
                "type": "attribute",
                "attribute": "dashboard_path",
                "name": "Dashboard File",
                "icon": "mdi:file-document"
            }
        ]
    }


def generate_basic_dashboard_config(hass: HomeAssistant) -> Dict[str, Any]:
    """
    Generate a basic dashboard configuration without custom cards.
    
    This fallback uses only standard Home Assistant Lovelace cards
    and does not require any custom integrations.
    """
    zones_data = hass.data.get(DOMAIN, {})

    # Get all zone names
    zone_names = []
    for zone in zones_data.values():
        if hasattr(zone, 'name'):
            zone_names.append(zone.name)

    # Build cards using only standard card types
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
    # Sanitize zone name for entity IDs using proper slugify
    zone_slug = slugify(zone_name)
    _LOGGER.debug(
        "Creating basic zone card for '%s' with slug '%s'",
        zone_name,
        zone_slug,
    )

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
                        "entity": f"binary_sensor.{zone_slug}_tidy",
                        "name": "Tidy Status",
                        "icon": "mdi:check-circle",
                    },
                    {
                        "entity": f"sensor.{zone_slug}_tasks",
                        "name": "Tasks to Complete",
                        "icon": "mdi:format-list-checkbox",
                    },
                    {
                        "entity": f"sensor.{zone_slug}_last_check",
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
                        "entity": f"sensor.{zone_slug}_tasks",
                        "state_not": "0",
                    }
                ],
                "card": {
                    "type": "markdown",
                    "content": (
                        f"{{% set tasks = state_attr('sensor.{zone_slug}_tasks', 'tasks') %}}\n"
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
                        "entity": f"sensor.{zone_slug}_tasks",
                        "state_not": "unavailable",
                    }
                ],
                "card": {
                    "type": "markdown",
                    "content": (
                        f"{{% set comment = state_attr('sensor.{zone_slug}_tasks', 'comment') %}}\n"
                        "{% if comment %}\n"
                        "**💬 Note:** {{ comment }}\n"
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


def get_required_custom_cards() -> List[str]:
    """
    Return list of custom cards required for the dashboard.
    
    Returns Bubble Card as the required custom card for the main dashboard.
    """
    return ["bubble-card"]


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
    
    This is the standard card type for the basic dashboard.
    """
    zone_slug = slugify(zone_name)
    
    return {
        "type": "entities",
        "title": f"🧹 {zone_name}",
        "entities": [
            {
                "entity": f"binary_sensor.{zone_slug}_tidy",
                "name": "Status",
            },
            {
                "entity": f"sensor.{zone_slug}_tasks",
                "name": "Task Count",
            },
            {
                "entity": f"sensor.{zone_slug}_last_check",
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

