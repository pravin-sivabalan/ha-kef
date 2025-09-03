"""Media player platform for KEF Speakers."""

from __future__ import annotations

import logging

from pykefcontrol import KefAsyncConnector

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, KEF_SOURCES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up KEF media player from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([KefMediaPlayer(coordinator, config_entry)])


class KefMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """KEF Speaker media player entity."""

    def __init__(self, coordinator, config_entry: ConfigEntry) -> None:
        """Initialize the KEF media player."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._host = config_entry.data[CONF_HOST]
        self._attr_unique_id = self._host
        self._kef_connector: KefAsyncConnector = coordinator.kef_connector

    @property
    def name(self) -> str:
        """Return the name of the media player."""
        if self.coordinator.data and "device_name" in self.coordinator.data:
            return self.coordinator.data["device_name"]
        return DEFAULT_NAME

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the media player."""
        if not self.coordinator.data or not self.coordinator.data.get("power"):
            return MediaPlayerState.OFF

        song_status = self.coordinator.data.get("song_status", "")
        if song_status == "playing":
            return MediaPlayerState.PLAYING
        elif song_status == "paused":
            return MediaPlayerState.PAUSED
        else:
            return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        if self.coordinator.data and "volume" in self.coordinator.data:
            return self.coordinator.data["volume"] / 100.0
        return None

    @property
    def is_volume_muted(self) -> bool | None:
        """Boolean if volume is currently muted."""
        if self.coordinator.data:
            return self.coordinator.data.get("mute", False)
        return None

    @property
    def source(self) -> str | None:
        """Name of the current input source."""
        if self.coordinator.data and "source" in self.coordinator.data:
            kef_source = self.coordinator.data["source"]
            return KEF_SOURCES.get(kef_source, kef_source)
        return None

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        return list(KEF_SOURCES.values())

    @property
    def media_title(self) -> str | None:
        """Title of current playing media."""
        if self.coordinator.data and "song_info" in self.coordinator.data:
            song_info = self.coordinator.data["song_info"]
            if isinstance(song_info, dict):
                return song_info.get("title")
        return None

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media."""
        if self.coordinator.data and "song_info" in self.coordinator.data:
            song_info = self.coordinator.data["song_info"]
            if isinstance(song_info, dict):
                return song_info.get("artist")
        return None

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        return (
            MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
        )

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        await self._kef_connector.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        await self._kef_connector.power_off()
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        kef_volume = int(volume * 100)
        self._kef_connector.volume = kef_volume
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute/unmute volume."""
        if mute:
            await self._kef_connector.mute()
        else:
            await self._kef_connector.unmute()
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        # Find KEF source key from display name
        kef_source = None
        for key, value in KEF_SOURCES.items():
            if value == source:
                kef_source = key
                break

        if kef_source:
            self._kef_connector.source = kef_source
            await self.coordinator.async_request_refresh()

    async def async_media_play(self) -> None:
        """Send play command."""
        await self._kef_connector.play()
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self._kef_connector.pause()
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self._kef_connector.next()
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self._kef_connector.prev()
        await self.coordinator.async_request_refresh()
