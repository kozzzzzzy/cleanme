from __future__ import annotations

import logging
from typing import Any, Dict, Callable

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.dt import as_local

from .const import (
    DOMAIN,
    ATTR_TASKS,
    ATTR_COMMENT,
    ATTR_FULL_ANALYSIS,
    ATTR_STATUS,
    ATTR_ERROR_MESSAGE,
    ATTR_IMAGE_SIZE,
    ATTR_API_RESPONSE_TIME,
    ATTR_ZONE_COUNT,
    ATTR_DASHBOARD_PATH,
    ATTR_DASHBOARD_LAST_GENERATED,
    ATTR_DASHBOARD_LAST_ERROR,
    ATTR_DASHBOARD_STATUS,
    ATTR_TASK_TOTAL,
    ATTR_READY,
    ATTR_LAST_CLEANED,
    ATTR_CLEAN_STREAK,
    ATTR_TOTAL_CLEANS,
    ATTR_MESSINESS_SCORE,
    ATTR_PRIORITY,
    ATTR_SNOOZED_UNTIL,
    ATTR_ZONES_NEEDING_ATTENTION,
    ATTR_NEXT_SCHEDULED_CHECK,
    ATTR_ALL_TIDY,
    SIGNAL_SYSTEM_STATE_UPDATED,
    SIGNAL_ZONE_STATE_UPDATED,
)
from .coordinator import CleanMeZone

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up CleanMe sensors for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.info(
        "Creating sensors for zone '%s' (entry_id: %s)",
        zone.name,
        entry.entry_id,
    )

    entities: list[SensorEntity] = [
        CleanMeTasksSensor(zone, entry),
        CleanMeLastCheckSensor(zone, entry),
        CleanMeLastCleanedSensor(zone, entry),
        CleanMeCleanStreakSensor(zone, entry),
        CleanMeTotalCleansSensor(zone, entry),
        CleanMeAICommentSensor(zone, entry),
        CleanMeMessinessScoreSensor(zone, entry),
    ]

    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("system_status_entity_added"):
        _LOGGER.info("Creating global CleanMe sensors")
        entities.append(CleanMeSystemStatusSensor(hass))
        entities.append(CleanMeTotalZonesSensor(hass))
        entities.append(CleanMeZonesNeedingAttentionSensor(hass))
        entities.append(CleanMeNextScheduledCheckSensor(hass))
        domain_data["system_status_entity_added"] = True

    for entity in entities:
        _LOGGER.debug(
            "Adding entity: unique_id=%s, has_device_info=%s",
            getattr(entity, "unique_id", None),
            hasattr(entity, "device_info"),
        )

    async_add_entities(entities)


class CleanMeBaseSensor(SensorEntity):
    """Base class for CleanMe zone sensors."""

    _attr_has_entity_name = True

    def __init__(self, zone: CleanMeZone, entry: ConfigEntry) -> None:
        self._zone = zone
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        self._zone.add_listener(self.async_write_ha_state)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info linking to the zone device."""
        return self._zone.device_info


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
            ATTR_MESSINESS_SCORE: self._zone.state.messiness_score,
            ATTR_LAST_CLEANED: self._zone.state.last_cleaned.isoformat() if self._zone.state.last_cleaned else None,
            ATTR_SNOOZED_UNTIL: self._zone.snooze_until.isoformat() if self._zone.snooze_until else None,
            ATTR_PRIORITY: self._zone.priority,
            ATTR_CLEAN_STREAK: self._zone.state.clean_streak,
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


class CleanMeLastCleanedSensor(CleanMeBaseSensor):
    """Sensor showing when the zone was last cleaned."""

    _attr_name = "Last cleaned"
    _attr_icon = "mdi:broom"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_last_cleaned"

    @property
    def native_value(self):
        """Return the last cleaned timestamp."""
        return self._zone.state.last_cleaned


class CleanMeCleanStreakSensor(CleanMeBaseSensor):
    """Sensor showing clean streak (consecutive days kept tidy)."""

    _attr_name = "Clean streak"
    _attr_icon = "mdi:fire"
    _attr_native_unit_of_measurement = "days"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_clean_streak"

    @property
    def native_value(self) -> int:
        """Return the clean streak."""
        return self._zone.state.clean_streak


class CleanMeTotalCleansSensor(CleanMeBaseSensor):
    """Sensor showing total times cleaned (all time)."""

    _attr_name = "Total cleans"
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "cleans"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_total_cleans"

    @property
    def native_value(self) -> int:
        """Return total cleans."""
        return self._zone.state.total_cleans


class CleanMeAICommentSensor(CleanMeBaseSensor):
    """Sensor showing AI comment about the room."""

    _attr_name = "AI comment"
    _attr_icon = "mdi:comment-text"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_ai_comment"

    @property
    def native_value(self) -> str | None:
        """Return the AI comment."""
        return self._zone.state.comment or "No comment yet"


class CleanMeMessinessScoreSensor(CleanMeBaseSensor):
    """Sensor showing messiness score (0-100)."""

    _attr_name = "Messiness score"
    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = "%"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_messiness_score"

    @property
    def native_value(self) -> int:
        """Return the messiness score."""
        return self._zone.state.messiness_score


class CleanMeGlobalBaseSensor(SensorEntity):
    """Base class for global CleanMe sensors."""

    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._unsubscribers: list[Callable[[], None]] = []

    async def async_added_to_hass(self) -> None:
        self._unsubscribers.append(
            async_dispatcher_connect(
                self._hass, SIGNAL_SYSTEM_STATE_UPDATED, self.async_write_ha_state
            )
        )
        self._unsubscribers.append(
            async_dispatcher_connect(
                self._hass, SIGNAL_ZONE_STATE_UPDATED, self.async_write_ha_state
            )
        )
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        while self._unsubscribers:
            unsub = self._unsubscribers.pop()
            unsub()

    def _get_zones(self) -> list[CleanMeZone]:
        """Get all CleanMe zones."""
        return [
            zone
            for zone in self._hass.data.get(DOMAIN, {}).values()
            if isinstance(zone, CleanMeZone)
        ]


class CleanMeSystemStatusSensor(CleanMeGlobalBaseSensor):
    """A single sensor summarizing overall CleanMe health."""

    _attr_name = "CleanMe System Status"
    _attr_icon = "mdi:shield-check"
    _attr_unique_id = "cleanme_system_status"

    @property
    def native_value(self) -> str:
        zones = self._get_zones()
        dashboard_state = self._hass.data.get(DOMAIN, {}).get("dashboard_state", {})

        if not zones:
            return "needs_zone"

        if dashboard_state.get(ATTR_DASHBOARD_STATUS) == "error":
            return "dashboard_error"

        if dashboard_state.get(ATTR_DASHBOARD_STATUS) in {"pending", "generated"}:
            return "dashboard_pending"

        return "ready"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        dashboard_state = self._hass.data.get(DOMAIN, {}).get("dashboard_state", {})
        zones = self._get_zones()

        last_generated = dashboard_state.get(ATTR_DASHBOARD_LAST_GENERATED)
        if last_generated:
            last_generated = as_local(last_generated).isoformat()

        task_total = sum(len(zone.state.tasks or []) for zone in zones)
        zones_needing_attention = [zone.name for zone in zones if zone.needs_attention]
        all_tidy = all(zone.state.tidy for zone in zones) if zones else False

        ready = bool(
            zones
            and dashboard_state.get(ATTR_DASHBOARD_STATUS) not in {"error", "unavailable"}
            and dashboard_state.get(ATTR_DASHBOARD_PATH)
        )

        return {
            ATTR_ZONE_COUNT: len(zones),
            ATTR_TASK_TOTAL: task_total,
            ATTR_ZONES_NEEDING_ATTENTION: zones_needing_attention,
            ATTR_ALL_TIDY: all_tidy,
            ATTR_DASHBOARD_PATH: dashboard_state.get(ATTR_DASHBOARD_PATH),
            ATTR_DASHBOARD_LAST_GENERATED: last_generated,
            ATTR_DASHBOARD_LAST_ERROR: dashboard_state.get(ATTR_DASHBOARD_LAST_ERROR),
            ATTR_DASHBOARD_STATUS: dashboard_state.get(ATTR_DASHBOARD_STATUS),
            ATTR_READY: ready,
        }


class CleanMeTotalZonesSensor(CleanMeGlobalBaseSensor):
    """Sensor showing total configured zones."""

    _attr_name = "CleanMe Total Zones"
    _attr_icon = "mdi:home-group"
    _attr_unique_id = "cleanme_total_zones"
    _attr_native_unit_of_measurement = "zones"

    @property
    def native_value(self) -> int:
        """Return total zone count."""
        return len(self._get_zones())


class CleanMeZonesNeedingAttentionSensor(CleanMeGlobalBaseSensor):
    """Sensor showing count of zones needing attention."""

    _attr_name = "CleanMe Zones Needing Attention"
    _attr_icon = "mdi:alert-circle"
    _attr_unique_id = "cleanme_zones_needing_attention"
    _attr_native_unit_of_measurement = "zones"

    @property
    def native_value(self) -> int:
        """Return count of messy zones."""
        zones = self._get_zones()
        return sum(1 for zone in zones if zone.needs_attention)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return list of zones needing attention."""
        zones = self._get_zones()
        return {
            "zones": [zone.name for zone in zones if zone.needs_attention],
        }


class CleanMeNextScheduledCheckSensor(CleanMeGlobalBaseSensor):
    """Sensor showing when the next scheduled check is."""

    _attr_name = "CleanMe Next Scheduled Check"
    _attr_icon = "mdi:calendar-clock"
    _attr_unique_id = "cleanme_next_scheduled_check"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self):
        """Return the next scheduled check time."""
        zones = self._get_zones()
        next_checks = [
            zone.next_scheduled_check
            for zone in zones
            if zone.next_scheduled_check is not None
        ]
        
        if not next_checks:
            return None
        
        return min(next_checks)
