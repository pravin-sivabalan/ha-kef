"""Config flow for KEF Speakers integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pykefcontrol import KefAsyncConnector

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class KefConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for KEF Speakers."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        
        # Validate the connection
        host = user_input[CONF_HOST]
        
        try:
            # Test connection to KEF speaker
            kef_connector = KefAsyncConnector(host)
            device_name = await kef_connector.device_name
            
            if not device_name:
                raise Exception("Could not get device name")
                
            _LOGGER.info("Successfully connected to KEF speaker: %s", device_name)
            
        except Exception as err:
            _LOGGER.error("Error connecting to KEF speaker at %s: %s", host, err)
            errors["base"] = "cannot_connect"
        else:
            # Check if already configured
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()
            
            # Create the config entry
            return self.async_create_entry(
                title=device_name or DEFAULT_NAME,
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )