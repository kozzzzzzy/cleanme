"""Number platform for CleanMe."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    DOMAIN,
    DEFAULT_CHECK_INTERVAL_HOURS,
)
from .coordinator import CleanMeZone

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe number entities for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.info(
        "Creating number entities for zone '%s' (entry_id: %s)",
        zone.name,
        entry.entry_id,
    )

    entities = [
        CleanMeCheckIntervalNumber(zone, entry),
    ]

    async_add_entities(entities)


class CleanMeCheckIntervalNumber(NumberEntity):
    """Number entity for check interval (hours)."""

    _attr_has_entity_name = True
    _attr_name = "Check Interval"
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 1
    _attr_native_max_value = 168  # 1 week
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "hours"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_check_interval"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info linking to the zone device."""
        return self._zone.device_info

    @property
    def native_value(self) -> float:
        """Return current check interval."""
        return self._zone.check_interval_hours

    async def async_set_native_value(self, value: float) -> None:
        """Set new check interval."""
        _LOGGER.info(
            "Setting check interval for zone '%s' to %s hours",
            self._zone.name,
            value,
        )
        await self._zone.async_set_check_interval(value)
