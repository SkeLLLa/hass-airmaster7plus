"""Config flow for AirMaster 7 Plus."""

from __future__ import annotations

import socket
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_ONLINE_TIMEOUT_S,
    CONF_UDP_PORT,
    DEFAULT_ONLINE_TIMEOUT_S,
    DEFAULT_UDP_PORT,
    DOMAIN,
)


def _port_bindable(port: int) -> bool:
    """Best-effort check that the UDP port can be bound."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("0.0.0.0", port))
    except OSError:
        return False
    finally:
        sock.close()
    return True


class Am7pConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step. Single instance — one UDP listener."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        if user_input is not None:
            port = user_input[CONF_UDP_PORT]
            bindable = await self.hass.async_add_executor_job(_port_bindable, port)
            if not bindable:
                errors["base"] = "port_unavailable"
            else:
                return self.async_create_entry(
                    title="AirMaster 7 Plus", data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_UDP_PORT, default=DEFAULT_UDP_PORT): cv.port,
                vol.Required(
                    CONF_ONLINE_TIMEOUT_S, default=DEFAULT_ONLINE_TIMEOUT_S
                ): cv.positive_int,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return Am7pOptionsFlow()


class Am7pOptionsFlow(OptionsFlow):
    """Handle options (edit timeout post-setup)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ONLINE_TIMEOUT_S,
                    default=current.get(
                        CONF_ONLINE_TIMEOUT_S, DEFAULT_ONLINE_TIMEOUT_S
                    ),
                ): cv.positive_int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
