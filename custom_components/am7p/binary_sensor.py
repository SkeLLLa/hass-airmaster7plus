"""Binary sensor platform for AirMaster 7 Plus (connectivity)."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_NEW_DEVICE
from .coordinator import Am7pUdpListener
from .entity import Am7pEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the connectivity binary sensor per discovered device."""
    listener: Am7pUdpListener = entry.runtime_data

    @callback
    def _add_device(ip: str) -> None:
        async_add_entities([Am7pOnlineSensor(listener, listener.devices[ip])])

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_NEW_DEVICE, _add_device)
    )
    for ip in list(listener.devices):
        _add_device(ip)


class Am7pOnlineSensor(Am7pEntity, BinarySensorEntity):
    """Connectivity sensor reflecting the device online flag."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_translation_key = "online"

    def __init__(self, listener, device) -> None:
        """Initialize."""
        super().__init__(listener, device)
        self._attr_unique_id = f"{device.ip}_online"

    @property
    def available(self) -> bool:
        """Connectivity sensor itself is always available."""
        return True

    @property
    def is_on(self) -> bool:
        """True when the device is online."""
        return self._device.online
