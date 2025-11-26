"""Button platform for CleanMe."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
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
    """Set up CleanMe button entities for a config entry."""
    zone: CleanMeZone = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.info(
        "Creating button entities for zone '%s' (entry_id: %s)",
        zone.name,
        entry.entry_id,
    )

    entities = [
        CleanMeCheckNowButton(zone, entry),
        CleanMeMarkCleanButton(zone, entry),
        CleanMeSnooze1hButton(zone, entry),
        CleanMeSnoozeTomorrowButton(zone, entry),
        CleanMeUnsnoozeButton(zone, entry),
    ]

    # Add global buttons only once
    domain_data = hass.data.setdefault(DOMAIN, {})
    if not domain_data.get("global_buttons_added"):
        _LOGGER.info("Creating global CleanMe button entities")
        entities.append(CleanMeCheckAllButton(hass))
        entities.append(CleanMeMarkAllCleanButton(hass))
        domain_data["global_buttons_added"] = True

    async_add_entities(entities)


class CleanMeZoneButton(ButtonEntity):
    """Base class for CleanMe zone buttons."""

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


class CleanMeCheckNowButton(CleanMeZoneButton):
    """Button to trigger an AI check."""

    _attr_name = "Check Now"
    _attr_icon = "mdi:camera-iris"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_check_now"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Check Now button pressed for zone '%s'", self._zone.name)
        await self._zone.async_request_check(reason="button")


class CleanMeMarkCleanButton(CleanMeZoneButton):
    """Button to mark zone as cleaned."""

    _attr_name = "Mark Clean"
    _attr_icon = "mdi:check-bold"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_mark_clean"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Mark Clean button pressed for zone '%s'", self._zone.name)
        await self._zone.async_mark_clean()


class CleanMeSnooze1hButton(CleanMeZoneButton):
    """Button to snooze zone for 1 hour."""

    _attr_name = "Snooze 1h"
    _attr_icon = "mdi:sleep"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_snooze_1h"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Snooze 1h button pressed for zone '%s'", self._zone.name)
        await self._zone.async_snooze(minutes=60)


class CleanMeSnoozeTomorrowButton(CleanMeZoneButton):
    """Button to snooze zone until tomorrow."""

    _attr_name = "Snooze Tomorrow"
    _attr_icon = "mdi:weather-night"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_snooze_tomorrow"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Snooze Tomorrow button pressed for zone '%s'", self._zone.name)
        # Snooze for 24 hours
        await self._zone.async_snooze(minutes=1440)


class CleanMeUnsnoozeButton(CleanMeZoneButton):
    """Button to cancel snooze for zone."""

    _attr_name = "Unsnooze"
    _attr_icon = "mdi:alarm-off"

    @property
    def unique_id(self) -> str:
        return f"{self._entry_id}_unsnooze"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Unsnooze button pressed for zone '%s'", self._zone.name)
        await self._zone.async_unsnooze()


class CleanMeCheckAllButton(ButtonEntity):
    """Button to check all zones at once."""

    _attr_has_entity_name = True
    _attr_name = "Check All Zones"
    _attr_icon = "mdi:camera-burst"
    _attr_unique_id = "cleanme_check_all"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._unsubscribers: list = []

    async def async_added_to_hass(self) -> None:
        self._unsubscribers.append(
            async_dispatcher_connect(
                self._hass, SIGNAL_SYSTEM_STATE_UPDATED, self.async_write_ha_state
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        while self._unsubscribers:
            unsub = self._unsubscribers.pop()
            unsub()

    async def async_press(self) -> None:
        """Handle button press - check all zones."""
        _LOGGER.info("Check All Zones button pressed")
        zones = [
            zone
            for zone in self._hass.data.get(DOMAIN, {}).values()
            if isinstance(zone, CleanMeZone)
        ]
        
        for zone in zones:
            await zone.async_request_check(reason="check_all")


class CleanMeMarkAllCleanButton(ButtonEntity):
    """Button to mark all zones as clean."""

    _attr_has_entity_name = True
    _attr_name = "Mark All Clean"
    _attr_icon = "mdi:check-all"
    _attr_unique_id = "cleanme_mark_all_clean"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._unsubscribers: list = []

    async def async_added_to_hass(self) -> None:
        self._unsubscribers.append(
            async_dispatcher_connect(
                self._hass, SIGNAL_SYSTEM_STATE_UPDATED, self.async_write_ha_state
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        while self._unsubscribers:
            unsub = self._unsubscribers.pop()
            unsub()

    async def async_press(self) -> None:
        """Handle button press - mark all zones as clean."""
        _LOGGER.info("Mark All Clean button pressed")
        zones = [
            zone
            for zone in self._hass.data.get(DOMAIN, {}).values()
            if isinstance(zone, CleanMeZone)
        ]
        
        for zone in zones:
            await zone.async_mark_clean()
