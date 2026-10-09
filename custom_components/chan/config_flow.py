"""Bind Chan to three entities from the same ESPHome robot."""

import probatio as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import (
    CONF_ACTIVE_ENTITY,
    CONF_DEVICE_ID,
    CONF_EXPRESSION_ENTITY,
    CONF_PHASE_ENTITY,
    DOMAIN,
    EXPRESSIONS,
)


class ChanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure one Chan per ESPHome device."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Select firmware endpoints, rejecting mixed devices and wrong entities."""
        errors = {}
        if user_input is not None:
            registry = er.async_get(self.hass)
            entries = [
                registry.async_get(user_input[key])
                for key in (CONF_ACTIVE_ENTITY, CONF_EXPRESSION_ENTITY, CONF_PHASE_ENTITY)
            ]
            if any(item is None or item.platform != "esphome" for item in entries):
                errors["base"] = "invalid_entities"
            elif not entries[0].device_id or len({item.device_id for item in entries}) != 1:
                errors["base"] = "mixed_devices"
            else:
                expression = self.hass.states.get(user_input[CONF_EXPRESSION_ENTITY])
                if expression is None or not set(EXPRESSIONS).issubset(
                    expression.attributes.get("options", [])
                ):
                    errors["base"] = "invalid_expressions"
                else:
                    device_id = entries[0].device_id
                    await self.async_set_unique_id(device_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Chan",
                        data={
                            CONF_ACTIVE_ENTITY: entries[0].id,
                            CONF_EXPRESSION_ENTITY: entries[1].id,
                            CONF_PHASE_ENTITY: entries[2].id,
                            CONF_DEVICE_ID: device_id,
                        },
                    )
        return self.async_show_form(step_id="user", data_schema=self._schema(), errors=errors)

    @callback
    def _schema(self):
        return vol.Schema(
            {
                vol.Required(CONF_ACTIVE_ENTITY): EntitySelector(
                    EntitySelectorConfig(domain="switch", integration="esphome")
                ),
                vol.Required(CONF_EXPRESSION_ENTITY): EntitySelector(
                    EntitySelectorConfig(domain="select", integration="esphome")
                ),
                vol.Required(CONF_PHASE_ENTITY): EntitySelector(
                    EntitySelectorConfig(domain="sensor", integration="esphome")
                ),
            }
        )
