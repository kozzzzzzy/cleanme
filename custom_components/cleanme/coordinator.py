from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client, event
from homeassistant.util.dt import utcnow
from homeassistant.components.camera import async_get_image
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_CAMERA_ENTITY,
    CONF_API_KEY,
    CONF_PERSONALITY,
    CONF_PICKINESS,
    CONF_CHECK_FREQUENCY,
    FREQUENCY_TO_RUNS,
    PERSONALITY_THOROUGH,
    SIGNAL_ZONE_STATE_UPDATED,
)
from .gemini_client import GeminiClient, GeminiClientError

_LOGGER = logging.getLogger(__name__)


@dataclass
class CleanMeState:
    """State data for a CleanMe zone."""
    tidy: bool = False
    tasks: List[str] = field(default_factory=list)
    comment: str | None = None
    severity: str = "medium"
    last_error: str | None = None
    last_checked: datetime | None = None
    image_size: int = 0
    api_response_time: float = 0.0
    full_analysis: Dict[str, Any] = field(default_factory=dict)

    @property
    def needs_tidy(self) -> bool:
        """Return True if the zone needs tidying."""
        return not self.tidy and bool(self.tasks)


class CleanMeZone:
    """One tidy zone (room/area)."""

    def __init__(self, hass: HomeAssistant, entry_id: str, name: str, data: Dict[str, Any]) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self._name = name

        self._camera_entity_id: str = data[CONF_CAMERA_ENTITY]
        self._personality: str = data.get(CONF_PERSONALITY, PERSONALITY_THOROUGH)
        self._pickiness: int = int(data.get(CONF_PICKINESS, 3))
        self._check_frequency: str = data.get(CONF_CHECK_FREQUENCY, "manual")

        # Calculate runs per day from frequency
        self._runs_per_day: int = FREQUENCY_TO_RUNS.get(self._check_frequency, 0)

        api_key = data.get(CONF_API_KEY) or ""
        self._gemini_client = GeminiClient(api_key)

        self._state = CleanMeState()
        self._listeners: list[Callable[[], None]] = []
        self._unsub_timer: Optional[Callable[[], None]] = None
        self._snooze_until: Optional[datetime] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def camera_entity_id(self) -> str:
        return self._camera_entity_id

    @property
    def personality(self) -> str:
        return self._personality

    @property
    def pickiness(self) -> int:
        return self._pickiness

    @property
    def state(self) -> CleanMeState:
        return self._state

    @property
    def needs_tidy(self) -> bool:
        return self._state.needs_tidy

    @property
    def snooze_until(self) -> Optional[datetime]:
        return self._snooze_until

    async def async_setup(self) -> None:
        """Set up timers if auto mode is enabled."""
        if self._runs_per_day > 0:
            self._setup_auto_timer()

    @callback
    def _setup_auto_timer(self) -> None:
        """Set up periodic checks based on runs/day."""
        if self._unsub_timer:
            self._unsub_timer()

        interval_hours = 24 / float(self._runs_per_day)
        interval = timedelta(hours=interval_hours)

        async def _handle(now) -> None:
            await self.async_request_check(reason="auto")

        self._unsub_timer = event.async_track_time_interval(
            self.hass, _handle, interval
        )

    async def async_unload(self) -> None:
        """Clean up on unload."""
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        self._listeners.clear()

    @callback
    def add_listener(self, listener: Callable[[], None]) -> None:
        """Register an entity listener."""
        self._listeners.append(listener)

    @callback
    def _notify_listeners(self) -> None:
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:
                continue
        async_dispatcher_send(self.hass, SIGNAL_ZONE_STATE_UPDATED)

    async def async_snooze(self, minutes: int) -> None:
        """Snooze auto checks for some minutes."""
        self._snooze_until = utcnow() + timedelta(minutes=minutes)

    async def async_clear_tasks(self) -> None:
        """Clear tasks and mark as tidy."""
        self._state.tasks = []
        self._state.tidy = True
        self._state.comment = "Tasks cleared manually."
        self._state.last_error = None
        self._state.last_checked = utcnow()
        self._notify_listeners()

    async def async_request_check(self, reason: str = "manual") -> None:
        """Run a check now (may be called by service or timer)."""
        now = utcnow()

        # Check if zone is snoozed
        if reason == "auto" and self._snooze_until and now < self._snooze_until:
            _LOGGER.debug("Zone %s is snoozed until %s", self._name, self._snooze_until)
            return

        try:
            image = await async_get_image(self.hass, self._camera_entity_id)
            image_bytes = image.content
        except Exception as err:
            _LOGGER.error("Failed to capture camera image for %s: %s", self._name, err)
            self._state.last_error = f"Failed to capture camera image: {err}"
            self._state.tidy = False
            self._state.last_checked = now
            self._notify_listeners()
            return

        session = aiohttp_client.async_get_clientsession(self.hass)

        try:
            result = await self._gemini_client.analyze_image(
                session=session,
                image_bytes=image_bytes,
                room_name=self._name,
                personality=self._personality,
                pickiness=self._pickiness,
            )
        except GeminiClientError as err:
            _LOGGER.error("Gemini API error for %s: %s", self._name, err)
            self._state.last_error = str(err)
            self._state.tidy = False
            self._state.last_checked = now
            self._notify_listeners()
            return
        except Exception as err:
            _LOGGER.exception("Unexpected error analyzing %s: %s", self._name, err)
            self._state.last_error = f"Unexpected error: {err}"
            self._state.tidy = False
            self._state.last_checked = now
            self._notify_listeners()
            return

        # Update state with results
        self._state.tidy = result.get("tidy", False)
        self._state.tasks = result.get("tasks", [])
        self._state.comment = result.get("comment", "")
        self._state.severity = result.get("severity", "medium")
        self._state.image_size = result.get("image_size", 0)
        self._state.api_response_time = result.get("api_response_time", 0.0)
        self._state.full_analysis = result
        self._state.last_error = None
        self._state.last_checked = now

        _LOGGER.info(
            "Zone %s analyzed: tidy=%s, tasks=%d, severity=%s",
            self._name,
            self._state.tidy,
            len(self._state.tasks),
            self._state.severity,
        )

        self._notify_listeners()
