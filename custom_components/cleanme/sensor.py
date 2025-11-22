from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    ATTR_TASKS,
    ATTR_COMMENT,
    ATTR_FULL_ANALYSIS,
    ATTR_STATUS,
    ATTR_ERROR_MESSAGE,
    ATTR_IMAGE_SIZE,
    ATTR_API_RESPONSE_TIME,
)
from .coordinator import CleanMeZone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe sensors for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        CleanMeTasksSensor(zone, entry),
        CleanMeLastCheckSensor(zone, entry),
    ]

    async_add_entities(entities)


class CleanMeBaseSensor(SensorEntity):
    """Base class for CleanMe sensors."""

    _attr_has_entity_name = True

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)


class CleanMeTasksSensor(CleanMeBaseSensor):
    """Sensor showing task count and task list."""

    _attr_name = "Tasks"
    _attr_icon = "mdi:format-list-checkbox"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_tasks"

    @property
    def native_value(self) -> int:
        """Return the number of tasks."""
        return len(self._zone.state.tasks or [])

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return task list and other details."""
        return {
            ATTR_TASKS: self._zone.state.tasks or [],
            ATTR_COMMENT: self._zone.state.comment or "",
            ATTR_FULL_ANALYSIS: self._zone.state.full_analysis or {},
        }


class CleanMeLastCheckSensor(CleanMeBaseSensor):
    """Sensor showing when the zone was last checked."""

    _attr_name = "Last check"
    _attr_icon = "mdi:clock-check-outline"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_last_check"

    @property
    def native_value(self):
        """Return the last check timestamp."""
        return self._zone.state.last_checked
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return check status and metadata."""
        attrs = {
            ATTR_STATUS: "success" if not self._zone.state.last_error else "error",
        }
        
        if self._zone.state.last_error:
            attrs[ATTR_ERROR_MESSAGE] = self._zone.state.last_error
        
        if self._zone.state.image_size > 0:
            attrs[ATTR_IMAGE_SIZE] = self._zone.state.image_size
        
        if self._zone.state.api_response_time > 0:
            attrs[ATTR_API_RESPONSE_TIME] = round(self._zone.state.api_response_time, 2)
        
        return attrs
