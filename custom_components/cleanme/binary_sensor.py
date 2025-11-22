from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, ATTR_PERSONALITY, ATTR_PICKINESS, ATTR_CAMERA_ENTITY, ATTR_LAST_CHECK, ATTR_SNOOZE_UNTIL
from .coordinator import CleanMeZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe binary sensors for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([CleanMeTidyBinarySensor(zone, entry)])


class CleanMeTidyBinarySensor(BinarySensorEntity):
    """Binary sensor: is the room tidy?"""

    _attr_has_entity_name = True
    _attr_name = "Tidy"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:broom"

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_tidy"

    @property
    def is_on(self) -> bool:
        """Return True if tidy (ON = Green), False if messy (OFF = Red)."""
        return self._zone.state.tidy

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attrs = {
            ATTR_PERSONALITY: self._zone.personality,
            ATTR_PICKINESS: self._zone.pickiness,
            ATTR_CAMERA_ENTITY: self._zone.camera_entity_id,
            ATTR_LAST_CHECK: self._zone.state.last_checked.isoformat() if self._zone.state.last_checked else None,
        }

        if self._zone.snooze_until:
            attrs[ATTR_SNOOZE_UNTIL] = self._zone.snooze_until.isoformat()

        return attrs
