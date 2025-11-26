"""Auto-generate Lovelace dashboard configuration for CleanMe zones.

This dashboard uses Mushroom Cards for a modern, beautiful UI.
Falls back to standard Home Assistant cards if Mushroom Cards are not available.
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
DASHBOARD_PATH = "clean-me"
DASHBOARD_BADGES: List[Any] = []


def generate_dashboard_config(hass: HomeAssistant) -> Dict[str, Any]:
    """
    Generate a complete Lovelace dashboard configuration for all CleanMe zones.
    
    Uses Mushroom Cards for a modern, beautiful interface with:
    - Mushroom template cards for status display
    - Mini-graph-card for messiness history
    - Conditional cards for alerts
    - Markdown for task lists and AI comments
    - Color-coded status indicators
    
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
    
    # 1. Header section with system status
    cards.append(_create_mushroom_header())
    cards.append(_create_mushroom_status_row())
    
    # 2. Alert section (conditional - only shown when zones need attention)
    cards.append(_create_alert_section())
    
    # 3. Zone cards with Mushroom design
    if zone_names:
        cards.append(_create_section_title("Your Zones"))
        for zone_name in zone_names:
            cards.append(_create_mushroom_zone_card(zone_name))
    
    # 4. Quick actions row
    cards.append(_create_section_title("Quick Actions"))
    cards.append(_create_mushroom_quick_actions())
    
    # 5. System info section
    cards.append(_create_section_title("System Info"))
    cards.append(_create_mushroom_system_info())

    # Build the complete dashboard configuration
    dashboard_config = {
        "title": DASHBOARD_TITLE,
        "icon": DASHBOARD_ICON,
        "path": DASHBOARD_PATH,
        "badges": DASHBOARD_BADGES,
        "cards": cards,
    }

    return dashboard_config


def _create_mushroom_header() -> Dict[str, Any]:
    """Create a Mushroom title card for the dashboard header."""
    return {
        "type": "custom:mushroom-title-card",
        "title": "🧹 CleanMe Dashboard",
        "subtitle": "Keep your home tidy with AI-powered room analysis",
    }


def _create_mushroom_status_row() -> Dict[str, Any]:
    """Create status overview with Mushroom chips showing house status."""
    return {
        "type": "horizontal-stack",
        "cards": [
            {
                "type": "custom:mushroom-template-card",
                "entity": "sensor.cleanme_system_status",
                "primary": "House Status",
                "secondary": "{{ states('sensor.cleanme_system_status') | replace('_', ' ') | title }}",
                "icon": "mdi:home-analytics",
                "icon_color": "{% if states('sensor.cleanme_system_status') == 'ready' %}green{% elif states('sensor.cleanme_system_status') == 'needs_zone' %}orange{% else %}red{% endif %}",
                "tap_action": {"action": "more-info"},
                "layout": "vertical",
            },
            {
                "type": "custom:mushroom-template-card",
                "entity": "binary_sensor.cleanme_ready",
                "primary": "System Ready",
                "secondary": "{% if is_state('binary_sensor.cleanme_ready', 'on') %}Online{% else %}Offline{% endif %}",
                "icon": "mdi:robot-vacuum",
                "icon_color": "{% if is_state('binary_sensor.cleanme_ready', 'on') %}green{% else %}red{% endif %}",
                "tap_action": {"action": "more-info"},
                "layout": "vertical",
            },
            {
                "type": "custom:mushroom-template-card",
                "entity": "sensor.cleanme_zones_needing_attention",
                "primary": "Attention",
                "secondary": "{{ states('sensor.cleanme_zones_needing_attention') }} zones",
                "icon": "mdi:alert-circle",
                "icon_color": "{% if states('sensor.cleanme_zones_needing_attention') | int > 0 %}red{% else %}green{% endif %}",
                "tap_action": {"action": "more-info"},
                "layout": "vertical",
            },
        ]
    }


def _create_alert_section() -> Dict[str, Any]:
    """Create a conditional alert card for zones needing attention."""
    return {
        "type": "conditional",
        "conditions": [
            {
                "entity": "sensor.cleanme_zones_needing_attention",
                "state_not": "0",
            }
        ],
        "card": {
            "type": "custom:mushroom-template-card",
            "entity": "sensor.cleanme_zones_needing_attention",
            "primary": "⚠️ Zones Need Attention",
            "secondary": "{{ state_attr('sensor.cleanme_zones_needing_attention', 'zones') | join(', ') }}",
            "icon": "mdi:alert",
            "icon_color": "red",
            "card_mod": {
                "style": """
                    ha-card {
                        background: rgba(var(--rgb-red), 0.1);
                        border: 1px solid rgba(var(--rgb-red), 0.3);
                    }
                """
            }
        }
    }


def _create_section_title(title: str) -> Dict[str, Any]:
    """Create a section title using Mushroom title card."""
    return {
        "type": "custom:mushroom-title-card",
        "title": title,
    }


def _create_mushroom_zone_card(zone_name: str) -> Dict[str, Any]:
    """Create a comprehensive Mushroom card for a single zone."""
    zone_slug = slugify(zone_name)
    _LOGGER.debug(
        "Creating Mushroom zone card for '%s' with slug '%s'",
        zone_name,
        zone_slug,
    )
    
    return {
        "type": "vertical-stack",
        "cards": [
            # Zone status header with Mushroom template card
            {
                "type": "custom:mushroom-template-card",
                "entity": f"binary_sensor.{zone_slug}_tidy",
                "primary": zone_name,
                "secondary": "{% if is_state(entity, 'on') %}✅ Tidy{% else %}🧹 Needs cleaning{% endif %}",
                "icon": "mdi:home",
                "icon_color": f"{{% if is_state('binary_sensor.{zone_slug}_tidy', 'on') %}}green{{% else %}}orange{{% endif %}}",
                "tap_action": {"action": "more-info"},
                "badge_icon": f"{{% if states('sensor.{zone_slug}_tasks') | int > 0 %}}mdi:numeric-{{{{ states('sensor.{zone_slug}_tasks') }}}}{{% endif %}}",
                "badge_color": "red",
            },
            # Messiness score gauge with mini-graph
            {
                "type": "custom:mini-graph-card",
                "entities": [
                    {
                        "entity": f"sensor.{zone_slug}_messiness_score",
                        "name": "Messiness",
                    }
                ],
                "name": "Messiness History",
                "hours_to_show": 24,
                "points_per_hour": 1,
                "line_color": "var(--primary-color)",
                "line_width": 2,
                "show": {
                    "name": True,
                    "icon": False,
                    "state": True,
                    "legend": False,
                    "fill": "fade",
                },
                "height": 80,
            },
            # Stats row with chips
            {
                "type": "custom:mushroom-chips-card",
                "chips": [
                    {
                        "type": "entity",
                        "entity": f"sensor.{zone_slug}_tasks",
                        "icon": "mdi:format-list-checkbox",
                        "content_info": "state",
                    },
                    {
                        "type": "entity",
                        "entity": f"sensor.{zone_slug}_clean_streak",
                        "icon": "mdi:fire",
                        "content_info": "state",
                    },
                    {
                        "type": "entity",
                        "entity": f"sensor.{zone_slug}_total_cleans",
                        "icon": "mdi:counter",
                        "content_info": "state",
                    },
                ],
                "alignment": "center",
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
                        "### 📋 Tasks\n"
                        "{% for task in tasks %}\n"
                        "- {{ task }}\n"
                        "{% endfor %}\n"
                        "{% endif %}"
                    ),
                },
            },
            # AI Comment section - reads FULL comment from attribute
            {
                "type": "conditional",
                "conditions": [
                    {
                        "entity": f"sensor.{zone_slug}_ai_comment",
                        "state_not": "unavailable",
                    },
                    {
                        "entity": f"sensor.{zone_slug}_ai_comment",
                        "state_not": "No comment yet",
                    },
                ],
                "card": {
                    "type": "markdown",
                    "content": (
                        f"{{% set full_comment = state_attr('sensor.{zone_slug}_ai_comment', 'full_comment') %}}\n"
                        f"{{% set comment = full_comment if full_comment else states('sensor.{zone_slug}_ai_comment') %}}\n"
                        "{% if comment %}\n"
                        "### 💬 AI Says\n"
                        "{{ comment }}\n"
                        "{% endif %}"
                    ),
                },
            },
            # Action buttons with Mushroom chips
            {
                "type": "custom:mushroom-chips-card",
                "chips": [
                    {
                        "type": "action",
                        "icon": "mdi:camera-iris",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.request_check",
                            "data": {
                                "zone": zone_name,
                            },
                        },
                    },
                    {
                        "type": "action",
                        "icon": "mdi:check-bold",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.clear_tasks",
                            "data": {
                                "zone": zone_name,
                            },
                        },
                    },
                    {
                        "type": "action",
                        "icon": "mdi:sleep",
                        "tap_action": {
                            "action": "call-service",
                            "service": "cleanme.snooze_zone",
                            "data": {
                                "zone": zone_name,
                                "duration_minutes": 60,
                            },
                        },
                    },
                ],
                "alignment": "center",
            },
        ],
    }


def _create_mushroom_quick_actions() -> Dict[str, Any]:
    """Create a row of quick action Mushroom chips."""
    return {
        "type": "custom:mushroom-chips-card",
        "chips": [
            {
                "type": "action",
                "icon": "mdi:plus-circle",
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "/config/integrations/integration/cleanme"
                },
            },
            {
                "type": "action",
                "icon": "mdi:cog",
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": "/config/integrations/integration/cleanme"
                },
            },
            {
                "type": "action",
                "icon": "mdi:refresh",
                "tap_action": {
                    "action": "call-service",
                    "service": "cleanme.regenerate_dashboard"
                },
            },
        ],
        "alignment": "center",
    }


def _create_mushroom_system_info() -> Dict[str, Any]:
    """Create system information section with Mushroom cards."""
    return {
        "type": "custom:mushroom-chips-card",
        "chips": [
            {
                "type": "entity",
                "entity": "sensor.cleanme_total_zones",
                "icon": "mdi:home-group",
                "content_info": "state",
            },
            {
                "type": "entity",
                "entity": "sensor.cleanme_next_scheduled_check",
                "icon": "mdi:calendar-clock",
                "content_info": "state",
            },
            {
                "type": "entity",
                "entity": "binary_sensor.cleanme_all_tidy",
                "icon": "mdi:check-circle",
            },
        ],
        "alignment": "center",
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
    
    Returns Mushroom Cards and mini-graph-card as the required custom cards.
    """
    return ["mushroom", "mini-graph-card"]


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

