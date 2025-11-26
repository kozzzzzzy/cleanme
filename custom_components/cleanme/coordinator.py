from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client, event
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.storage import Store
from homeassistant.util.dt import utcnow
from homeassistant.components.camera import async_get_image
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    DOMAIN,
    CONF_CAMERA_ENTITY,
    CONF_API_KEY,
    CONF_PERSONALITY,
    CONF_PICKINESS,
    CONF_CHECK_FREQUENCY,
    FREQUENCY_TO_RUNS,
    PERSONALITY_FRIENDLY,
    SIGNAL_ZONE_STATE_UPDATED,
    DEFAULT_CHECK_INTERVAL_HOURS,
    DEFAULT_OVERDUE_THRESHOLD_HOURS,
    DEFAULT_PRIORITY,
    PRIORITY_OPTIONS,
    STORAGE_KEY,
    STORAGE_VERSION,
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
    
    # Extended state fields
    last_cleaned: datetime | None = None
    clean_streak: int = 0
    total_cleans: int = 0
    messiness_score: int = 0  # 0-100 based on tasks/severity
    
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
        self._personality: str = data.get(CONF_PERSONALITY, PERSONALITY_FRIENDLY)
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
        
        # New configurable fields
        self._priority: str = data.get("priority", DEFAULT_PRIORITY)
        self._check_interval_hours: float = data.get("check_interval", DEFAULT_CHECK_INTERVAL_HOURS)
        self._next_scheduled_check: Optional[datetime] = None
        
        # Storage for persistence
        self._store: Store | None = None

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
    
    @property
    def is_snoozed(self) -> bool:
        """Return True if zone is currently snoozed."""
        if self._snooze_until is None:
            return False
        return utcnow() < self._snooze_until
    
    @property
    def priority(self) -> str:
        return self._priority
    
    @property
    def check_interval_hours(self) -> float:
        return self._check_interval_hours
    
    @property
    def next_scheduled_check(self) -> Optional[datetime]:
        return self._next_scheduled_check
    
    @property
    def needs_attention(self) -> bool:
        """Return True if zone needs attention (messy and not snoozed)."""
        if self.is_snoozed:
            return False
        return self._state.needs_tidy
    
    @property
    def is_overdue(self) -> bool:
        """Return True if zone hasn't been cleaned in too long."""
        if self._state.last_cleaned is None:
            # Never cleaned - not overdue until first check
            if self._state.last_checked is None:
                return False
            # Check against last check time if never cleaned
            hours_since_check = (utcnow() - self._state.last_checked).total_seconds() / 3600
            return hours_since_check > DEFAULT_OVERDUE_THRESHOLD_HOURS
        
        hours_since_clean = (utcnow() - self._state.last_cleaned).total_seconds() / 3600
        return hours_since_clean > DEFAULT_OVERDUE_THRESHOLD_HOURS

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this zone."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=self._name,
            manufacturer="CleanMe",
            model="AI Tidy Zone",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_setup(self) -> None:
        """Set up timers if auto mode is enabled and load persisted state."""
        # Initialize storage
        self._store = Store(self.hass, STORAGE_VERSION, f"{STORAGE_KEY}.{self.entry_id}")
        await self._async_load_state()
        
        if self._runs_per_day > 0:
            self._setup_auto_timer()

    async def _async_load_state(self) -> None:
        """Load persisted state from storage."""
        if self._store is None:
            return
        
        data = await self._store.async_load()
        if data:
            # Restore extended state fields
            if "last_cleaned" in data and data["last_cleaned"]:
                self._state.last_cleaned = datetime.fromisoformat(data["last_cleaned"])
            self._state.clean_streak = data.get("clean_streak", 0)
            self._state.total_cleans = data.get("total_cleans", 0)
            self._priority = data.get("priority", DEFAULT_PRIORITY)
            self._check_interval_hours = data.get("check_interval", DEFAULT_CHECK_INTERVAL_HOURS)
            
            _LOGGER.debug(
                "Loaded persisted state for zone %s: streak=%d, total=%d",
                self._name,
                self._state.clean_streak,
                self._state.total_cleans,
            )

    async def _async_save_state(self) -> None:
        """Save state to storage for persistence."""
        if self._store is None:
            return
        
        data = {
            "last_cleaned": self._state.last_cleaned.isoformat() if self._state.last_cleaned else None,
            "clean_streak": self._state.clean_streak,
            "total_cleans": self._state.total_cleans,
            "priority": self._priority,
            "check_interval": self._check_interval_hours,
        }
        await self._store.async_save(data)

    @callback
    def _setup_auto_timer(self) -> None:
        """Set up periodic checks based on runs/day."""
        if self._unsub_timer:
            self._unsub_timer()

        interval_hours = 24 / float(self._runs_per_day)
        interval = timedelta(hours=interval_hours)
        
        # Set next scheduled check
        self._next_scheduled_check = utcnow() + interval

        async def _handle(now) -> None:
            await self.async_request_check(reason="auto")
            # Update next scheduled check
            self._next_scheduled_check = utcnow() + interval

        self._unsub_timer = event.async_track_time_interval(
            self.hass, _handle, interval
        )

    async def async_unload(self) -> None:
        """Clean up on unload."""
        # Save state before unloading
        await self._async_save_state()
        
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
            except Exception as err:
                _LOGGER.error(
                    "Error notifying listener for zone %s: %s",
                    self._name,
                    err,
                    exc_info=True,
                )
                continue
        async_dispatcher_send(self.hass, SIGNAL_ZONE_STATE_UPDATED)

    async def async_snooze(self, minutes: int) -> None:
        """Snooze auto checks for some minutes."""
        self._snooze_until = utcnow() + timedelta(minutes=minutes)
        self._notify_listeners()
    
    async def async_unsnooze(self) -> None:
        """Cancel snooze for this zone."""
        self._snooze_until = None
        self._notify_listeners()

    async def async_clear_tasks(self) -> None:
        """Clear tasks and mark as tidy."""
        self._state.tasks = []
        self._state.tidy = True
        self._state.comment = "Tasks cleared manually."
        self._state.last_error = None
        self._state.last_checked = utcnow()
        self._notify_listeners()
    
    async def async_mark_clean(self) -> None:
        """Mark zone as cleaned by user."""
        now = utcnow()
        
        # Update clean streak
        if self._state.last_cleaned:
            hours_since_clean = (now - self._state.last_cleaned).total_seconds() / 3600
            # Keep streak if cleaned within 48 hours
            if hours_since_clean <= DEFAULT_OVERDUE_THRESHOLD_HOURS:
                self._state.clean_streak += 1
            else:
                self._state.clean_streak = 1
        else:
            self._state.clean_streak = 1
        
        self._state.total_cleans += 1
        self._state.last_cleaned = now
        self._state.tasks = []
        self._state.tidy = True
        self._state.messiness_score = 0
        self._state.comment = "Marked clean by user."
        self._state.last_error = None
        
        # Persist state
        await self._async_save_state()
        self._notify_listeners()
        
        _LOGGER.info(
            "Zone %s marked clean: streak=%d, total=%d",
            self._name,
            self._state.clean_streak,
            self._state.total_cleans,
        )
    
    async def async_set_priority(self, priority: str) -> None:
        """Set the priority level for this zone."""
        if priority not in PRIORITY_OPTIONS:
            _LOGGER.warning("Invalid priority '%s' for zone %s", priority, self._name)
            return
        
        self._priority = priority
        await self._async_save_state()
        self._notify_listeners()
    
    async def async_set_check_interval(self, hours: float) -> None:
        """Set the check interval in hours."""
        if hours < 1:
            hours = 1
        if hours > 168:  # Max 1 week
            hours = 168
        
        self._check_interval_hours = hours
        await self._async_save_state()
        self._notify_listeners()
    
    async def async_set_personality(self, personality: str) -> None:
        """Set the AI personality for this zone."""
        self._personality = personality
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
        
        # Calculate messiness score (0-100)
        self._state.messiness_score = self._calculate_messiness_score()

        _LOGGER.info(
            "Zone %s analyzed: tidy=%s, tasks=%d, severity=%s, messiness=%d",
            self._name,
            self._state.tidy,
            len(self._state.tasks),
            self._state.severity,
            self._state.messiness_score,
        )

        self._notify_listeners()
    
    def _calculate_messiness_score(self) -> int:
        """Calculate messiness score from 0-100 based on tasks and severity."""
        if self._state.tidy:
            return 0
        
        # Base score from number of tasks
        task_count = len(self._state.tasks)
        if task_count == 0:
            return 0
        
        # Each task adds 10-20 points depending on severity
        severity_multiplier = {
            "low": 10,
            "medium": 15,
            "high": 20,
        }
        multiplier = severity_multiplier.get(self._state.severity, 15)
        
        score = min(100, task_count * multiplier)
        return score
