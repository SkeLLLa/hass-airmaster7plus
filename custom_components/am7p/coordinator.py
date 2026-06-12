"""UDP listener + device registry for AirMaster 7 Plus."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    SCAN_INTERVAL_S,
    SIGNAL_NEW_DEVICE,
    SIGNAL_UPDATE,
)
from .parser import parse_packet

_LOGGER = logging.getLogger(__name__)


@dataclass
class Am7pDevice:
    """State for a single AM7P device, keyed by source IP."""

    ip: str
    name: str
    last_packet_monotonic: float = 0.0
    last_packet_at: datetime | None = None
    payload: dict = field(default_factory=dict)
    online: bool = False

    @property
    def age_s(self) -> int:
        """Seconds since last packet."""
        if not self.last_packet_monotonic:
            return 999999
        return int(time.monotonic() - self.last_packet_monotonic)


class Am7pUdpListener(asyncio.DatagramProtocol):
    """Owns the UDP socket; dispatches device discovery and updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        udp_port: int,
        online_timeout_s: int,
        name_map: dict[str, str],
    ) -> None:
        """Initialize the listener."""
        self.hass = hass
        self.udp_port = udp_port
        self.online_timeout_s = online_timeout_s
        self.name_map = name_map
        self.devices: dict[str, Am7pDevice] = {}
        self._transport: asyncio.BaseTransport | None = None
        self._cancel_interval = None
        self._closed: asyncio.Future[None] = hass.loop.create_future()

    async def async_start(self) -> None:
        """Open the datagram endpoint and start the availability timer."""
        loop = self.hass.loop
        self._transport, _ = await loop.create_datagram_endpoint(
            lambda: self,
            local_addr=("0.0.0.0", self.udp_port),
        )
        self._cancel_interval = async_track_time_interval(
            self.hass,
            self._async_recompute_online,
            timedelta(seconds=SCAN_INTERVAL_S),
        )
        _LOGGER.info("AM7P UDP listener started on port %s", self.udp_port)

    async def async_stop(self) -> None:
        """Close the transport and wait until the socket is released."""
        if self._cancel_interval is not None:
            self._cancel_interval()
            self._cancel_interval = None
        if self._transport is not None:
            self._transport.close()
            try:
                await asyncio.wait_for(self._closed, timeout=2)
            except TimeoutError:
                _LOGGER.warning(
                    "Timed out while closing AM7P UDP listener on port %s",
                    self.udp_port,
                )
            finally:
                self._transport = None
        _LOGGER.info("AM7P UDP listener stopped")

    def _name_for(self, ip: str) -> str:
        """Device name from config map, else auto from last IP octet."""
        if ip in self.name_map:
            return self.name_map[ip]
        return f"am7p_{ip.rsplit('.', 1)[-1]}"

    # --- DatagramProtocol callbacks (run in event loop thread) ---

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle an incoming UDP datagram."""
        payload = parse_packet(data)
        if payload is None:
            return
        ip = addr[0]
        device = self.devices.get(ip)
        is_new = device is None
        if device is None:
            device = Am7pDevice(ip=ip, name=self._name_for(ip))
            self.devices[ip] = device

        device.payload = payload
        device.last_packet_monotonic = time.monotonic()
        device.last_packet_at = dt_util.utcnow()
        device.online = True

        if is_new:
            async_dispatcher_send(self.hass, SIGNAL_NEW_DEVICE, ip)
        async_dispatcher_send(self.hass, SIGNAL_UPDATE.format(ip))

    def error_received(self, exc: Exception) -> None:
        """Log transport-level errors."""
        _LOGGER.debug("AM7P UDP error: %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        """Mark the listener transport as closed."""
        if exc is not None:
            _LOGGER.debug("AM7P UDP listener connection lost: %s", exc)
        if not self._closed.done():
            self._closed.set_result(None)

    # --- periodic availability recompute ---

    @callback
    def _async_recompute_online(self, _now) -> None:
        """Recompute online flags and dispatch availability updates."""
        for ip, device in self.devices.items():
            online = device.age_s <= self.online_timeout_s
            if online != device.online:
                device.online = online
                async_dispatcher_send(self.hass, SIGNAL_UPDATE.format(ip))
