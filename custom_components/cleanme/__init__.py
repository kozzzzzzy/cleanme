from __future__ import annotations

from typing import Any, Dict
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_REQUEST_CHECK,
    SERVICE_SNOOZE_ZONE,
    SERVICE_CLEAR_TASKS,
    SERVICE_ADD_ZONE,
    ATTR_ZONE,
    ATTR_DURATION_MINUTES,
    CONF_NAME,
    CONF_CAMERA_ENTITY,
    CONF_PERSONALITY,
    CONF_PICKINESS,
    CONF_CHECK_FREQUENCY,
    CONF_API_KEY,
    PERSONALITY_OPTIONS,
    FREQUENCY_OPTIONS,
)
from .coordinator import CleanMeZone
from . import dashboard as cleanme_dashboard

LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up from YAML (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a CleanMe config entry."""
    hass.data.setdefault(DOMAIN, {})

    zone = CleanMeZone(
        hass=hass,
        entry_id=entry.entry_id,
        name=entry.data.get("name") or entry.title,
        data=entry.data,
    )

    hass.data[DOMAIN][entry.entry_id] = zone

    await zone.async_setup()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_REQUEST_CHECK):
        _register_services(hass)

    # Generate and log dashboard configuration
    LOGGER.info("CleanMe: Registering dashboard for zone '%s'", entry.title)
    try:
        dashboard_config = cleanme_dashboard.generate_dashboard_config(hass)
        # Ensure domain data is initialized before storing dashboard config
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        hass.data[DOMAIN]["dashboard_config"] = dashboard_config
        LOGGER.info("CleanMe: Dashboard generated with %d cards", len(dashboard_config.get("cards", [])))
    except Exception as e:
        LOGGER.error("CleanMe: Failed to generate dashboard: %s", e)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a CleanMe entry."""
    zone: CleanMeZone = hass.data[DOMAIN].pop(entry.entry_id, None)
    if zone:
        await zone.async_unload()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_REQUEST_CHECK)
        hass.services.async_remove(DOMAIN, SERVICE_SNOOZE_ZONE)
        hass.services.async_remove(DOMAIN, SERVICE_CLEAR_TASKS)
        hass.services.async_remove(DOMAIN, SERVICE_ADD_ZONE)
    else:
        # Regenerate dashboard when zones change
        try:
            dashboard_config = cleanme_dashboard.generate_dashboard_config(hass)
            # Ensure domain data is initialized before storing dashboard config
            if DOMAIN not in hass.data:
                hass.data[DOMAIN] = {}
            hass.data[DOMAIN]["dashboard_config"] = dashboard_config
            LOGGER.info("CleanMe: Dashboard updated after zone removal")
        except Exception as e:
            LOGGER.error("CleanMe: Failed to update dashboard: %s", e)

    return unload_ok


def _find_zone_by_name(hass: HomeAssistant, zone_name: str) -> CleanMeZone | None:
    for zone in hass.data.get(DOMAIN, {}).values():
        if isinstance(zone, CleanMeZone) and hasattr(zone, 'name') and zone.name == zone_name:
            return zone
    return None


def _register_services(hass: HomeAssistant) -> None:
    """Register CleanMe domain services."""

    async def handle_request_check(call: ServiceCall) -> None:
        zone_name = call.data[ATTR_ZONE]
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            return
        await zone.async_request_check(reason="service")

    async def handle_snooze(call: ServiceCall) -> None:
        zone_name = call.data[ATTR_ZONE]
        minutes = int(call.data[ATTR_DURATION_MINUTES])
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            return
        await zone.async_snooze(minutes)

    async def handle_clear_tasks(call: ServiceCall) -> None:
        zone_name = call.data[ATTR_ZONE]
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            return
        await zone.async_clear_tasks()

    async def handle_add_zone(call: ServiceCall) -> None:
        """Dynamically add a new zone via service call."""
        data = {
            CONF_NAME: call.data[CONF_NAME],
            CONF_CAMERA_ENTITY: call.data[CONF_CAMERA_ENTITY],
            CONF_PERSONALITY: call.data.get(CONF_PERSONALITY, "thorough"),
            CONF_PICKINESS: call.data.get(CONF_PICKINESS, 3),
            CONF_CHECK_FREQUENCY: call.data.get(CONF_CHECK_FREQUENCY, "manual"),
            CONF_API_KEY: call.data[CONF_API_KEY],
        }

        # Create a new config entry programmatically
        await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=data,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST_CHECK,
        handle_request_check,
        vol.Schema({vol.Required(ATTR_ZONE): str}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SNOOZE_ZONE,
        handle_snooze,
        vol.Schema(
            {
                vol.Required(ATTR_ZONE): str,
                vol.Required(ATTR_DURATION_MINUTES): vol.All(
                    int, vol.Range(min=1, max=1440)
                ),
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_TASKS,
        handle_clear_tasks,
        vol.Schema({vol.Required(ATTR_ZONE): str}),
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_ZONE,
        handle_add_zone,
        vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_CAMERA_ENTITY): cv.entity_id,
                vol.Required(CONF_PERSONALITY): vol.In(list(PERSONALITY_OPTIONS.keys())),
                vol.Required(CONF_PICKINESS): vol.All(int, vol.Range(min=1, max=5)),
                vol.Required(CONF_CHECK_FREQUENCY): vol.In(list(FREQUENCY_OPTIONS.keys())),
                vol.Required(CONF_API_KEY): str,
            }
        ),
    )
