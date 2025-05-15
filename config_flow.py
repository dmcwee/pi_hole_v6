"""Config flow to configure the Pi-hole integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from hole.exceptions import HoleConnectionError, HoleError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_LOCATION,
    CONF_NAME,
    CONF_PORT,
    CONF_SSL,
    CONF_VERIFY_SSL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DEFAULT_API_KEY,
    DEFAULT_LOCATION,
    DEFAULT_NAME,
    DEFAULT_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

# from hole import Hole
from .v6 import HoleV6 as Hole

_LOGGER = logging.getLogger(__name__)


class PiHoleFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Pi-hole config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._config: dict = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            self._config = {
                CONF_HOST: f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}",
                CONF_NAME: user_input[CONF_NAME],
                CONF_LOCATION: user_input[CONF_LOCATION],
                CONF_SSL: user_input[CONF_SSL],
                CONF_VERIFY_SSL: user_input[CONF_VERIFY_SSL],
                CONF_API_KEY: user_input[CONF_API_KEY],
            }
            _LOGGER.debug("User input: %s", user_input)

            self._async_abort_entries_match(
                {
                    CONF_HOST: f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}",
                    CONF_LOCATION: user_input[CONF_LOCATION],
                }
            )

            if not (errors := await self._async_try_connect()):
                _LOGGER.debug("Called _async_try_connect() and creating entry")
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=self._config
                )

            _LOGGER.debug("Errors: %s", errors)
            if CONF_API_KEY in errors:
                return await self.async_step_api_key()

        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
                    vol.Required(
                        CONF_PORT, default=user_input.get(CONF_PORT, 80)
                    ): vol.Coerce(int),
                    vol.Required(
                        CONF_NAME, default=user_input.get(CONF_NAME, DEFAULT_NAME)
                    ): str,
                    vol.Required(
                        CONF_LOCATION,
                        default=user_input.get(CONF_LOCATION, DEFAULT_LOCATION),
                    ): str,
                    vol.Required(
                        CONF_API_KEY,
                        default=user_input.get(CONF_API_KEY, DEFAULT_API_KEY),
                    ): str,
                    vol.Required(
                        CONF_SSL,
                        default=user_input.get(CONF_SSL, DEFAULT_SSL),
                    ): bool,
                    vol.Required(
                        CONF_VERIFY_SSL,
                        default=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                    ): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_api_key(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle step to setup API key."""
        errors = {}
        if user_input is not None:
            self._config[CONF_API_KEY] = user_input[CONF_API_KEY]
            if not (errors := await self._async_try_connect()):
                return self.async_create_entry(
                    title=self._config[CONF_NAME],
                    data=self._config,
                )

        return self.async_show_form(
            step_id="api_key",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        self._config = dict(entry_data)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Perform reauth confirm upon an API authentication error."""
        errors = {}
        if user_input is not None:
            self._config = {**self._config, CONF_API_KEY: user_input[CONF_API_KEY]}
            if not (errors := await self._async_try_connect()):
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(), data=self._config
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            description_placeholders={
                CONF_HOST: self._config[CONF_HOST],
                CONF_LOCATION: self._config[CONF_LOCATION],
            },
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def _async_try_connect(self) -> dict[str, str]:
        session = async_get_clientsession(self.hass, self._config[CONF_VERIFY_SSL])
        _LOGGER.debug("config details: Host(%s)", self._config[CONF_HOST])
        pi_hole = Hole(
            host=self._config[CONF_HOST],
            session=session,
            location=self._config[CONF_LOCATION],
            verify_tls=self._config[CONF_SSL],
            password=self._config.get(CONF_API_KEY),
        )
        _LOGGER.debug("Testing the connection to %s", pi_hole.base_url)
        try:
            await pi_hole.get_data()
        except HoleConnectionError as ecx:
            _LOGGER.debug("Connection failed: %s", ecx)
            return {"base": "cannot_connect"}
        except HoleError as ex:
            _LOGGER.debug("Connection failed: %s", ex)
            return {"base": "cannot_connect"}

        if not isinstance(pi_hole.data, dict):
            _LOGGER.debug("pi_hold.data is not instance of dict")
            return {CONF_API_KEY: "invalid_auth"}

        _LOGGER.debug("pi_hold.data is instance of dict: %s", pi_hole.data)
        return {}
