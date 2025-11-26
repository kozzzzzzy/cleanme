from __future__ import annotations

import logging
from typing import Any, Dict, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util.dt import as_local

from .const import (
    DOMAIN,
    ATTR_PERSONALITY,
    ATTR_PICKINESS,
    ATTR_CAMERA_ENTITY,
    ATTR_LAST_CHECK,
    ATTR_SNOOZE_UNTIL,
    ATTR_ZONE_COUNT,
    ATTR_DASHBOARD_PATH,
    ATTR_DASHBOARD_LAST_GENERATED,
    ATTR_DASHBOARD_LAST_ERROR,
    ATTR_DASHBOARD_STATUS,
    ATTR_READY,
    ATTR_SNOOZED_UNTIL,
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
    """Set up CleanMe binary sensors for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.info(
        "Creating binary sensors for zone '%s' (entry_id: %s)",
        zone.name,
        entry.entry_id,
    )

    entities = [
        CleanMeTidyBinarySensor(zone, entry),
        CleanMeNeedsAttentionBinarySensor(zone, entry),
        CleanMeOverdueBinarySensor(zone, entry),
        CleanMeSnoozedBinarySensor(zone, entry),
    ]

    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("ready_entity_added"):
        _LOGGER.info("Creating global CleanMe binary sensors")
        entities.append(CleanMeReadyBinarySensor(hass))
        entities.append(CleanMeAllTidyBinarySensor(hass))
        domain_data["ready_entity_added"] = True

    for entity in entities:
        _LOGGER.debug(
            "Adding entity: unique_id=%s, has_device_info=%s",
            getattr(entity, "unique_id", None),
            hasattr(entity, "device_info"),
        )

    async_add_entities(entities)


class CleanMeZoneBinarySensor(BinarySensorEntity):
    """Base class for CleanMe zone binary sensors."""

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


class CleanMeTidyBinarySensor(CleanMeZoneBinarySensor):
    """Binary sensor: is the room tidy?"""

    _attr_name = "Tidy"
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:broom"

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


class CleanMeNeedsAttentionBinarySensor(CleanMeZoneBinarySensor):
    """Binary sensor: does the room need attention?"""

    _attr_name = "Needs attention"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:alert-circle"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_needs_attention"

    @property
    def is_on(self) -> bool:
        """Return True if zone needs attention (messy and not snoozed)."""
        return self._zone.needs_attention


class CleanMeOverdueBinarySensor(CleanMeZoneBinarySensor):
    """Binary sensor: is the zone overdue for cleaning?"""

    _attr_name = "Overdue"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:clock-alert"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_overdue"

    @property
    def is_on(self) -> bool:
        """Return True if zone hasn't been cleaned in too long."""
        return self._zone.is_overdue


class CleanMeSnoozedBinarySensor(CleanMeZoneBinarySensor):
    """Binary sensor: is the zone currently snoozed?"""

    _attr_name = "Snoozed"
    _attr_icon = "mdi:sleep"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_snoozed"

    @property
    def is_on(self) -> bool:
        """Return True if zone is currently snoozed."""
        return self._zone.is_snoozed

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return snooze end time."""
        if self._zone.snooze_until:
            return {ATTR_SNOOZED_UNTIL: self._zone.snooze_until.isoformat()}
        return {}


class CleanMeGlobalBinarySensor(BinarySensorEntity):
    """Base class for global CleanMe binary sensors."""

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


class CleanMeReadyBinarySensor(CleanMeGlobalBinarySensor):
    """Binary sensor showing CleanMe overall readiness."""

    _attr_name = "CleanMe Ready"
    _attr_icon = "mdi:check-circle"
    _attr_unique_id = "cleanme_ready"

    @property
    def is_on(self) -> bool:
        zones = self._get_zones()
        dashboard_state = self._hass.data.get(DOMAIN, {}).get("dashboard_state", {})

        has_dashboard = bool(dashboard_state.get(ATTR_DASHBOARD_PATH))
        healthy = dashboard_state.get(ATTR_DASHBOARD_STATUS) not in {"error", "unavailable"}

        return bool(zones and has_dashboard and healthy)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        dashboard_state = self._hass.data.get(DOMAIN, {}).get("dashboard_state", {})
        zones = self._get_zones()

        last_generated = dashboard_state.get(ATTR_DASHBOARD_LAST_GENERATED)
        if last_generated:
            last_generated = as_local(last_generated).isoformat()

        ready = self.is_on

        return {
            ATTR_ZONE_COUNT: len(zones),
            ATTR_DASHBOARD_PATH: dashboard_state.get(ATTR_DASHBOARD_PATH),
            ATTR_DASHBOARD_LAST_GENERATED: last_generated,
            ATTR_DASHBOARD_LAST_ERROR: dashboard_state.get(ATTR_DASHBOARD_LAST_ERROR),
            ATTR_READY: ready,
        }


class CleanMeAllTidyBinarySensor(CleanMeGlobalBinarySensor):
    """Binary sensor showing if all zones are tidy."""

    _attr_name = "CleanMe All Tidy"
    _attr_icon = "mdi:home-heart"
    _attr_unique_id = "cleanme_all_tidy"

    @property
    def is_on(self) -> bool:
        """Return True if all zones are tidy."""
        zones = self._get_zones()
        if not zones:
            return False
        return all(zone.state.tidy for zone in zones)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return zone status summary."""
        zones = self._get_zones()
        tidy_zones = [zone.name for zone in zones if zone.state.tidy]
        messy_zones = [zone.name for zone in zones if not zone.state.tidy]
        
        return {
            "tidy_zones": tidy_zones,
            "messy_zones": messy_zones,
            ATTR_ZONE_COUNT: len(zones),
        }
