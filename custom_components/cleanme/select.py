"""Select platform for CleanMe."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    DOMAIN,
    PRIORITY_OPTIONS,
    PERSONALITY_OPTIONS,
    DEFAULT_PRIORITY,
    PERSONALITY_FRIENDLY,
)
from .coordinator import CleanMeZone

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe select entities for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.info(
        "Creating select entities for zone '%s' (entry_id: %s)",
        zone.name,
        entry.entry_id,
    )

    entities = [
        CleanMePrioritySelect(zone, entry),
        CleanMePersonalitySelect(zone, entry),
    ]

    async_add_entities(entities)


class CleanMePrioritySelect(SelectEntity):
    """Select entity for zone priority."""

    _attr_has_entity_name = True
    _attr_name = "Priority"
    _attr_icon = "mdi:flag"
    _attr_options = list(PRIORITY_OPTIONS.keys())

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_priority"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info linking to the zone device."""
        return self._zone.device_info

    @property
    def current_option(self) -> str:
        """Return current priority."""
        return self._zone.priority

    async def async_select_option(self, option: str) -> None:
        """Set new priority."""
        _LOGGER.info(
            "Setting priority for zone '%s' to '%s'",
            self._zone.name,
            option,
        )
        await self._zone.async_set_priority(option)


class CleanMePersonalitySelect(SelectEntity):
    """Select entity for AI personality."""

    _attr_has_entity_name = True
    _attr_name = "AI Personality"
    _attr_icon = "mdi:robot-happy"
    _attr_options = list(PERSONALITY_OPTIONS.keys())

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_ai_personality"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info linking to the zone device."""
        return self._zone.device_info

    @property
    def current_option(self) -> str:
        """Return current personality."""
        return self._zone.personality

    async def async_select_option(self, option: str) -> None:
        """Set new personality."""
        _LOGGER.info(
            "Setting AI personality for zone '%s' to '%s'",
            self._zone.name,
            option,
        )
        await self._zone.async_set_personality(option)
