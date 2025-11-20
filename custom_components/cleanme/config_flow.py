from __future__ import annotations

from typing import Any, Dict

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_CAMERA_ENTITY,
    CONF_PROVIDER,
    CONF_MODEL,
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_MODE,
    CONF_RUNS_PER_DAY,
    MODE_MANUAL,
    MODE_AUTO,
    PROVIDER_OPTIONS,
    PROVIDER_OPENAI,
    DEFAULT_MODEL_OPENAI,
    RUNS_PER_DAY_OPTIONS,
)


LOGGER = logging.getLogger(__name__)


def _default_model(provider: str) -> str:
    if provider == PROVIDER_OPENAI:
        return DEFAULT_MODEL_OPENAI
    return ""


class CleanMeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CleanMe."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                name = user_input[CONF_NAME]
                await self.async_set_unique_id(f"{DOMAIN}_{name.lower()}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data=user_input,
                )
            except Exception:  # pragma: no cover - defensive guard for runtime issues
                LOGGER.exception("CleanMe config flow failed")
                errors["base"] = "unknown"

        provider_default = PROVIDER_OPENAI

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_CAMERA_ENTITY): cv.entity_id,
                vol.Required(CONF_MODE, default=MODE_MANUAL): vol.In(
                    [MODE_MANUAL, MODE_AUTO]
                ),
                vol.Required(CONF_RUNS_PER_DAY, default=1): vol.In(RUNS_PER_DAY_OPTIONS),
                vol.Required(CONF_PROVIDER, default=provider_default): vol.In(
                    list(PROVIDER_OPTIONS.keys())
                ),
                vol.Required(CONF_MODEL, default=_default_model(provider_default)): str,
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_BASE_URL, default=""): str,
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
        if user_input is not None:
            data = {**self._entry.data, **user_input}
            return self.async_create_entry(title="", data=data)

        data = {**self._entry.data, **self._entry.options}

        provider = data.get(CONF_PROVIDER, PROVIDER_OPENAI)

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=data.get(CONF_NAME, self._entry.title)): str,
                vol.Required(
                    CONF_CAMERA_ENTITY,
                    default=data.get(CONF_CAMERA_ENTITY, ""),
                ): cv.entity_id,
                vol.Required(CONF_MODE, default=data.get(CONF_MODE, MODE_MANUAL)): vol.In(
                    [MODE_MANUAL, MODE_AUTO]
                ),
                vol.Required(
                    CONF_RUNS_PER_DAY,
                    default=int(data.get(CONF_RUNS_PER_DAY, 1)),
                ): vol.In(RUNS_PER_DAY_OPTIONS),
                vol.Required(CONF_PROVIDER, default=provider): vol.In(
                    list(PROVIDER_OPTIONS.keys())
                ),
                vol.Required(
                    CONF_MODEL, default=data.get(CONF_MODEL, _default_model(provider))
                ): str,
                vol.Required(CONF_API_KEY, default=data.get(CONF_API_KEY, "")): str,
                vol.Optional(CONF_BASE_URL, default=data.get(CONF_BASE_URL, "")): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
