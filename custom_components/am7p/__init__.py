"""The AirMaster 7 Plus integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_NAME_MAP,
    CONF_ONLINE_TIMEOUT_S,
    CONF_UDP_PORT,
    DEFAULT_ONLINE_TIMEOUT_S,
    DEFAULT_UDP_PORT,
    DOMAIN,
)
from .coordinator import Am7pUdpListener

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AirMaster 7 Plus from a config entry."""
    options = {**entry.data, **entry.options}
    udp_port = options.get(CONF_UDP_PORT, DEFAULT_UDP_PORT)
    online_timeout_s = options.get(CONF_ONLINE_TIMEOUT_S, DEFAULT_ONLINE_TIMEOUT_S)
    name_map = options.get(CONF_NAME_MAP, {})

    listener = Am7pUdpListener(hass, udp_port, online_timeout_s, name_map)
    try:
        await listener.async_start()
    except OSError as err:
        _LOGGER.error("Failed to bind UDP port %s: %s", udp_port, err)
        return False

    entry.runtime_data = listener

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        listener: Am7pUdpListener = entry.runtime_data
        await listener.async_stop()
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
