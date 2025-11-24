from __future__ import annotations

from typing import Any
import logging
from logging.handlers import RotatingFileHandler
import os

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.dt import utcnow

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
    ATTR_ZONE_COUNT,
    ATTR_DASHBOARD_LAST_ERROR,
    ATTR_DASHBOARD_LAST_GENERATED,
    ATTR_DASHBOARD_PATH,
    ATTR_DASHBOARD_STATUS,
    SIGNAL_SYSTEM_STATE_UPDATED,
    SIGNAL_ZONE_STATE_UPDATED,
)
from .coordinator import CleanMeZone
from . import dashboard as cleanme_dashboard

LOGGER = logging.getLogger(__name__)

# Check if PyYAML is available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    LOGGER.warning("CleanMe: PyYAML not available, YAML dashboard export disabled")


def _get_dashboard_state(hass: HomeAssistant) -> dict[str, Any]:
    """Return mutable dashboard state dict stored in hass.data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    return domain_data.setdefault(
        "dashboard_state",
        {
            ATTR_DASHBOARD_PATH: None,
            ATTR_DASHBOARD_LAST_GENERATED: None,
            ATTR_DASHBOARD_LAST_ERROR: None,
            ATTR_DASHBOARD_STATUS: "pending",
            "panel_registered": False,
        },
    )


async def async_setup_cleanme_logger(hass: HomeAssistant):
    """Setup dedicated CleanMe log file without blocking the event loop."""
    logger = logging.getLogger("custom_components.cleanme")

    # Avoid duplicate handlers
    if any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler for /config/cleanme.log
    log_file = hass.config.path("cleanme.log")

    def _create_handler():
        handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        return handler

    file_handler = await hass.async_add_executor_job(_create_handler)

    logger.addHandler(file_handler)
    logger.info("=" * 50)
    logger.info("CleanMe logging initialized")
    logger.info("=" * 50)

    return logger


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up from YAML (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a CleanMe config entry."""
    hass.data.setdefault(DOMAIN, {})

    await async_setup_cleanme_logger(hass)
    LOGGER.info("CleanMe: Setting up zone '%s' (entry_id: %s)", entry.title, entry.entry_id)

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
    dashboard_state = _get_dashboard_state(hass)

    try:
        dashboard_config = cleanme_dashboard.generate_dashboard_config(hass)
        hass.data[DOMAIN]["dashboard_config"] = dashboard_config
        dashboard_state[ATTR_DASHBOARD_STATUS] = "generated"
        LOGGER.info("CleanMe: Dashboard generated with %d cards", len(dashboard_config.get("cards", [])))

        # Generate YAML dashboard file
        await _regenerate_dashboard_yaml(hass)
    except Exception as e:
        dashboard_state[ATTR_DASHBOARD_STATUS] = "error"
        dashboard_state[ATTR_DASHBOARD_LAST_ERROR] = str(e)
        async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)
        LOGGER.error("CleanMe: Failed to generate dashboard: %s", e)
    
    # Register the dashboard as a UI panel if not already registered
    if not hass.data[DOMAIN].get("dashboard_panel_registered"):
        try:
            components = getattr(hass, "components", None)

            # Check if frontend component is available
            if not components or not hasattr(components, "frontend"):
                LOGGER.warning("CleanMe: Frontend component not available, skipping dashboard panel registration")
                return True

            # Create a panel for CleanMe
            await components.frontend.async_register_built_in_panel(
                component_name="lovelace",
                sidebar_title="CleanMe",
                sidebar_icon="mdi:broom",
                frontend_url_path="cleanme",
                require_admin=False,
                config={"mode": "storage"},
            )
            
            # Store the dashboard for the panel
            hass.data[DOMAIN]["dashboard_panel_registered"] = True
            dashboard_state["panel_registered"] = True
            async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)
            LOGGER.info("CleanMe: Dashboard panel registered in sidebar")
        except Exception as e:
            LOGGER.error("CleanMe: Failed to register dashboard panel: %s", e)

    async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)

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
        hass.services.async_remove(DOMAIN, "update_zone_config")
        hass.services.async_remove(DOMAIN, "delete_zone")
        hass.services.async_remove(DOMAIN, "regenerate_dashboard")
        hass.services.async_remove(DOMAIN, "export_basic_dashboard")

        # Remove dashboard panel when all zones are unloaded
        if hass.data[DOMAIN].get("dashboard_panel_registered"):
            try:
                components = getattr(hass, "components", None)
                # Check if frontend component is available
                if components and hasattr(components, "frontend"):
                    await components.frontend.async_remove_panel("cleanme")
                    LOGGER.info("CleanMe: Dashboard panel removed from sidebar")
                else:
                    LOGGER.warning("CleanMe: Frontend component not available, skipping dashboard panel removal")

                hass.data[DOMAIN]["dashboard_panel_registered"] = False
                dashboard_state = _get_dashboard_state(hass)
                dashboard_state["panel_registered"] = False
            except Exception as e:
                LOGGER.error("CleanMe: Failed to remove dashboard panel: %s", e)
    else:
        # Regenerate dashboard when zones change
        try:
            dashboard_config = cleanme_dashboard.generate_dashboard_config(hass)
            hass.data[DOMAIN]["dashboard_config"] = dashboard_config
            LOGGER.info("CleanMe: Dashboard updated after zone removal")

            # Regenerate dashboard YAML
            await _regenerate_dashboard_yaml(hass)
        except Exception as e:
            LOGGER.error("CleanMe: Failed to update dashboard: %s", e)

    async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)

    return unload_ok


def _find_zone_by_name(hass: HomeAssistant, zone_name: str) -> CleanMeZone | None:
    for zone in hass.data.get(DOMAIN, {}).values():
        if isinstance(zone, CleanMeZone) and hasattr(zone, 'name') and zone.name == zone_name:
            return zone
    return None


async def _regenerate_dashboard_yaml(hass: HomeAssistant) -> None:
    """Generate/update the YAML dashboard file for CleanMe."""
    dashboard_state = _get_dashboard_state(hass)

    if not YAML_AVAILABLE:
        LOGGER.debug("CleanMe: Skipping YAML generation (PyYAML not available)")
        dashboard_state[ATTR_DASHBOARD_LAST_ERROR] = "PyYAML not available"
        dashboard_state[ATTR_DASHBOARD_STATUS] = "unavailable"
        dashboard_state[ATTR_DASHBOARD_LAST_GENERATED] = utcnow()
        async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)
        return

    try:
        # Generate dashboard config
        dashboard_config = cleanme_dashboard.generate_dashboard_config(hass)
        
        # Build full Lovelace view YAML
        yaml_content = {
            "title": dashboard_config["title"],
            "path": dashboard_config["path"],
            "icon": dashboard_config["icon"],
            "badges": [],
            "cards": dashboard_config["cards"]
        }

        # Write to /config/dashboards/cleanme.yaml
        dashboards_dir = hass.config.path("dashboards")

        def _write_yaml() -> str:
            os.makedirs(dashboards_dir, mode=0o755, exist_ok=True)
            yaml_file = os.path.join(dashboards_dir, "cleanme.yaml")
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    yaml_content,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            return yaml_file

        yaml_file = await hass.async_add_executor_job(_write_yaml)

        dashboard_state[ATTR_DASHBOARD_PATH] = yaml_file
        dashboard_state[ATTR_DASHBOARD_LAST_GENERATED] = utcnow()
        dashboard_state[ATTR_DASHBOARD_LAST_ERROR] = None
        dashboard_state[ATTR_DASHBOARD_STATUS] = "written"
        async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)
        LOGGER.info("CleanMe: Dashboard YAML written to %s", yaml_file)

        try:
            hass.components.persistent_notification.create(
                (
                    "Your CleanMe dashboard has been written to:\n"
                    f"`{yaml_file}`\n\n"
                    "To use it, go to **Settings → Dashboards → Add dashboard**, "
                    "choose **YAML**, and select this file as the source. You can "
                    "then pin it to the sidebar as \"CleanMe\"."
                ),
                title="CleanMe dashboard ready",
                notification_id="cleanme_dashboard_ready",
            )
        except Exception as err:
            LOGGER.warning(
                "CleanMe: Unable to create dashboard notification: %s", err
            )
    except Exception as e:
        LOGGER.error("CleanMe: Failed to write dashboard YAML: %s", e)
        dashboard_state[ATTR_DASHBOARD_LAST_ERROR] = str(e)
        dashboard_state[ATTR_DASHBOARD_LAST_GENERATED] = utcnow()
        dashboard_state[ATTR_DASHBOARD_STATUS] = "error"
        async_dispatcher_send(hass, SIGNAL_SYSTEM_STATE_UPDATED)


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

    async def handle_update_zone_config(call: ServiceCall) -> None:
        """Update zone configuration from dashboard."""
        zone_name = call.data["zone"]
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            LOGGER.warning("CleanMe: Zone '%s' not found for update", zone_name)
            return
        
        # Get the config entry for this zone
        entry = hass.config_entries.async_get_entry(zone.entry_id)
        if not entry:
            LOGGER.warning("CleanMe: Config entry not found for zone '%s'", zone_name)
            return
        
        # Build updated data dict
        updated_data = dict(entry.data)
        
        if "pickiness" in call.data:
            updated_data[CONF_PICKINESS] = call.data["pickiness"]
        if "personality" in call.data:
            updated_data[CONF_PERSONALITY] = call.data["personality"]
        if "check_frequency" in call.data:
            updated_data[CONF_CHECK_FREQUENCY] = call.data["check_frequency"]
        if "camera_entity" in call.data:
            updated_data[CONF_CAMERA_ENTITY] = call.data["camera_entity"]
        
        # Update the entry
        hass.config_entries.async_update_entry(entry, data=updated_data)
        # Reload is required for the zone coordinator to pick up new config
        await hass.config_entries.async_reload(entry.entry_id)
        
        # Regenerate dashboard YAML
        await _regenerate_dashboard_yaml(hass)
        
        LOGGER.info("CleanMe: Updated config for zone '%s'", zone_name)

    async def handle_delete_zone(call: ServiceCall) -> None:
        """Delete a zone completely."""
        zone_name = call.data["zone"]
        zone = _find_zone_by_name(hass, zone_name)
        if not zone:
            LOGGER.warning("CleanMe: Zone '%s' not found for deletion", zone_name)
            return
        
        entry = hass.config_entries.async_get_entry(zone.entry_id)
        if entry:
            await hass.config_entries.async_remove(entry.entry_id)
            LOGGER.info("CleanMe: Deleted zone '%s'", zone_name)
            
            # Regenerate dashboard YAML
            await _regenerate_dashboard_yaml(hass)

    async def handle_regenerate_dashboard(call: ServiceCall) -> None:
        """Manually trigger dashboard YAML regeneration."""
        await _regenerate_dashboard_yaml(hass)
        LOGGER.info("CleanMe: Dashboard YAML regenerated")

    async def handle_export_basic_dashboard(call: ServiceCall) -> None:
        """Export a basic dashboard without custom cards."""
        if not YAML_AVAILABLE:
            LOGGER.error("CleanMe: PyYAML not available, cannot export dashboard")
            return

        try:
            # Generate basic dashboard config
            dashboard_config = cleanme_dashboard.generate_basic_dashboard_config(hass)

            # Write to /config/dashboards/cleanme-basic.yaml
            dashboards_dir = hass.config.path("dashboards")

            def _write_basic() -> str:
                os.makedirs(dashboards_dir, mode=0o755, exist_ok=True)
                yaml_file = os.path.join(dashboards_dir, "cleanme-basic.yaml")
                with open(yaml_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        dashboard_config,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )
                return yaml_file

            yaml_file = await hass.async_add_executor_job(_write_basic)

            LOGGER.info("CleanMe: Basic dashboard YAML written to %s", yaml_file)
        except Exception as e:
            LOGGER.error("CleanMe: Failed to write basic dashboard YAML: %s", e)


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

    hass.services.async_register(
        DOMAIN,
        "update_zone_config",
        handle_update_zone_config,
        vol.Schema(
            {
                vol.Required("zone"): str,
                vol.Optional("pickiness"): vol.All(int, vol.Range(min=1, max=5)),
                vol.Optional("personality"): vol.In(list(PERSONALITY_OPTIONS.keys())),
                vol.Optional("check_frequency"): vol.In(list(FREQUENCY_OPTIONS.keys())),
                vol.Optional("camera_entity"): cv.entity_id,
            }
        ),
    )

    hass.services.async_register(
        DOMAIN,
        "delete_zone",
        handle_delete_zone,
        vol.Schema({vol.Required("zone"): str}),
    )

    hass.services.async_register(
        DOMAIN,
        "regenerate_dashboard",
        handle_regenerate_dashboard,
        vol.Schema({}),
    )

    hass.services.async_register(
        DOMAIN,
        "export_basic_dashboard",
        handle_export_basic_dashboard,
        vol.Schema({}),
    )
