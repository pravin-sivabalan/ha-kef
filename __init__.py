"""KEF Speakers integration for Home Assistant."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from pykefcontrol import KefAsyncConnector

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KEF Speakers from a config entry."""
    host = entry.data[CONF_HOST]

    # Create KEF connector
    kef_connector = KefAsyncConnector(host)

    # Create coordinator
    coordinator = KefDataUpdateCoordinator(hass, kef_connector)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class KefDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching KEF speaker data."""

    def __init__(self, hass: HomeAssistant, kef_connector: KefAsyncConnector) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.kef_connector = kef_connector

    async def _async_update_data(self) -> dict:
        """Fetch data from KEF speaker."""
        try:
            # Get all speaker data
            data = {
                "status": await self.kef_connector.status,
                "volume": await self.kef_connector.volume,
                "source": await self.kef_connector.source,
                "speaker_name": await self.kef_connector.speaker_name,
                "song_status": await self.kef_connector.song_status,
                "song_info": await self.kef_connector.get_song_information(),
            }

            _LOGGER.debug("KEF speaker data: %s", data)
            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with KEF speaker: {err}") from err
