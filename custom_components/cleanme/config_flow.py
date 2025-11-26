from __future__ import annotations

from typing import Any, Dict

import logging
import uuid

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import selector
from homeassistant.helpers.storage import Store

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_CAMERA_ENTITY,
    CONF_API_KEY,
    CONF_PERSONALITY,
    CONF_PICKINESS,
    CONF_CHECK_FREQUENCY,
    PERSONALITY_OPTIONS,
    PERSONALITY_FRIENDLY,
    FREQUENCY_OPTIONS,
    FREQUENCY_MANUAL,
)
from .gemini_client import GeminiClient


LOGGER = logging.getLogger(__name__)

# Global API key storage
STORAGE_KEY_CONFIG = "cleanme.config"
STORAGE_VERSION_CONFIG = 1


async def async_get_stored_api_key(hass) -> str | None:
    """Get stored API key from global storage."""
    store = Store(hass, STORAGE_VERSION_CONFIG, STORAGE_KEY_CONFIG)
    data = await store.async_load()
    return data.get("api_key") if data else None


async def async_store_api_key(hass, api_key: str) -> None:
    """Store API key for future zones."""
    store = Store(hass, STORAGE_VERSION_CONFIG, STORAGE_KEY_CONFIG)
    data = await store.async_load() or {}
    data["api_key"] = api_key
    await store.async_save(data)


class CleanMeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CleanMe."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        # Get stored API key for pre-filling
        stored_api_key = await async_get_stored_api_key(self.hass)

        if user_input is not None:
            try:
                LOGGER.info("CleanMe: Starting config flow validation for zone '%s'", user_input.get(CONF_NAME))
                
                # Validate API key
                api_key = user_input[CONF_API_KEY]
                session = aiohttp_client.async_get_clientsession(self.hass)
                client = GeminiClient(api_key)

                LOGGER.info("CleanMe: Validating Gemini API key...")
                is_valid = await client.validate_api_key(session)
                if not is_valid:
                    LOGGER.error("CleanMe: API key validation failed")
                    errors["base"] = "invalid_api_key"
                else:
                    LOGGER.info("CleanMe: API key validated successfully")
                    
                    # Store the API key globally for future zones
                    await async_store_api_key(self.hass, api_key)
                    
                    name = user_input[CONF_NAME]
                    await self.async_set_unique_id(f"{DOMAIN}_{name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}")
                    self._abort_if_unique_id_configured()

                    LOGGER.info("CleanMe: Creating config entry for zone '%s' with camera '%s'", 
                               name, user_input.get(CONF_CAMERA_ENTITY))
                    return self.async_create_entry(
                        title=name,
                        data=user_input,
                    )
            except Exception as err:
                LOGGER.exception("CleanMe config flow failed: %s", err)
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_CAMERA_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="camera")
                ),
                vol.Required(CONF_PERSONALITY, default=PERSONALITY_FRIENDLY): vol.In(
                    list(PERSONALITY_OPTIONS.keys())
                ),
                vol.Required(CONF_PICKINESS, default=3): vol.All(
                    int, vol.Range(min=1, max=5)
                ),
                vol.Required(CONF_CHECK_FREQUENCY, default=FREQUENCY_MANUAL): vol.In(
                    list(FREQUENCY_OPTIONS.keys())
                ),
                vol.Required(CONF_API_KEY, default=stored_api_key or ""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return CleanMeOptionsFlow(config_entry)


class CleanMeOptionsFlow(config_entries.OptionsFlow):
    """Handle options for existing entry."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                LOGGER.info("CleanMe: Updating options for zone '%s'", user_input.get(CONF_NAME))
                
                # Validate API key if changed
                api_key = user_input[CONF_API_KEY]
                old_api_key = self._entry.data.get(CONF_API_KEY, "")

                if api_key != old_api_key:
                    LOGGER.info("CleanMe: API key changed, validating new key...")
                    session = aiohttp_client.async_get_clientsession(self.hass)
                    client = GeminiClient(api_key)

                    is_valid = await client.validate_api_key(session)
                    if not is_valid:
                        LOGGER.error("CleanMe: New API key validation failed")
                        errors["base"] = "invalid_api_key"
                    else:
                        LOGGER.info("CleanMe: New API key validated successfully")

                if not errors:
                    # Update the config entry data
                    self.hass.config_entries.async_update_entry(
                        self._entry,
                        data={**self._entry.data, **user_input}
                    )
                    # Trigger reload of the entry to apply changes
                    LOGGER.info("CleanMe: Reloading config entry to apply changes")
                    await self.hass.config_entries.async_reload(self._entry.entry_id)
                    return self.async_abort(reason="reconfigure_successful")
            except Exception as err:
                LOGGER.exception("CleanMe options flow failed: %s", err)
                errors["base"] = "unknown"

        data = {**self._entry.data, **self._entry.options}

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=data.get(CONF_NAME, self._entry.title)): str,
                vol.Required(
                    CONF_CAMERA_ENTITY,
                    default=data.get(CONF_CAMERA_ENTITY, ""),
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="camera")
                ),
                vol.Required(
                    CONF_PERSONALITY,
                    default=data.get(CONF_PERSONALITY, PERSONALITY_FRIENDLY),
                ): vol.In(list(PERSONALITY_OPTIONS.keys())),
                vol.Required(
                    CONF_PICKINESS,
                    default=int(data.get(CONF_PICKINESS, 3)),
                ): vol.All(int, vol.Range(min=1, max=5)),
                vol.Required(
                    CONF_CHECK_FREQUENCY,
                    default=data.get(CONF_CHECK_FREQUENCY, FREQUENCY_MANUAL),
                ): vol.In(list(FREQUENCY_OPTIONS.keys())),
                vol.Required(CONF_API_KEY, default=data.get(CONF_API_KEY, "")): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)