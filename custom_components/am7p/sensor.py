"""Sensor platform for AirMaster 7 Plus."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LAST_PACKET_DESCRIPTION,
    SENSOR_DESCRIPTIONS,
    SIGNAL_NEW_DEVICE,
)
from .coordinator import Am7pUdpListener
from .entity import Am7pEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors, adding entities for each discovered device."""
    listener: Am7pUdpListener = entry.runtime_data

    @callback
    def _add_device(ip: str) -> None:
        device = listener.devices[ip]
        entities: list[SensorEntity] = [
            Am7pSensor(listener, device, desc) for desc in SENSOR_DESCRIPTIONS
        ]
        entities.append(Am7pLastPacketSensor(listener, device))
        async_add_entities(entities)

    entry.async_on_unload(
        async_dispatcher_connect(hass, SIGNAL_NEW_DEVICE, _add_device)
    )

    # Add any devices already discovered before platform setup.
    for ip in list(listener.devices):
        _add_device(ip)


class Am7pSensor(Am7pEntity, SensorEntity):
    """A measurement sensor backed by the coordinator's latest payload."""

    def __init__(self, listener, device, description: SensorEntityDescription) -> None:
        """Initialize."""
        super().__init__(listener, device)
        self.entity_description = description
        self._attr_unique_id = f"{device.ip}_{description.key}"

    @property
    def native_value(self):
        """Return the latest value for this sensor's key."""
        return self._device.payload.get(self.entity_description.key)


class Am7pLastPacketSensor(Am7pEntity, SensorEntity):
    """Diagnostic: timestamp of the last received packet."""

    entity_description = LAST_PACKET_DESCRIPTION
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, listener, device) -> None:
        """Initialize."""
        super().__init__(listener, device)
        self._attr_unique_id = f"{device.ip}_last_packet"

    @property
    def available(self) -> bool:
        """Available once the device has sent at least one packet."""
        return self._device.last_packet_at is not None

    @property
    def native_value(self):
        """Timestamp of the last received packet."""
        return self._device.last_packet_at
