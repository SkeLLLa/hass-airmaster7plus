"""Base entity for AirMaster 7 Plus."""

from __future__ import annotations

from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, SIGNAL_UPDATE
from .coordinator import Am7pDevice, Am7pUdpListener


class Am7pEntity(Entity):
    """Common base: device grouping + dispatcher-driven state writes."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, listener: Am7pUdpListener, device: Am7pDevice) -> None:
        """Initialize."""
        self._listener = listener
        self._ip = device.ip
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.ip)},
            name=device.name,
            manufacturer="AirMaster",
            model="7 Plus",
        )

    @property
    def _device(self) -> Am7pDevice:
        return self._listener.devices[self._ip]

    @property
    def available(self) -> bool:
        """Available while the device is considered online."""
        return self._device.online

    async def async_added_to_hass(self) -> None:
        """Subscribe to updates for this device's IP."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_UPDATE.format(self._ip),
                self.async_write_ha_state,
            )
        )
