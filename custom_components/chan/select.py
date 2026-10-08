"""Constrained manual expression control for hardware testing."""

from homeassistant.components.select import SelectEntity

from .const import EXPRESSIONS
from .entity import ChanEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ChanExpressionSelect(entry.runtime_data)])


class ChanExpressionSelect(ChanEntity, SelectEntity):
    """Change expressions only during an active interaction."""

    _attr_options = list(EXPRESSIONS)
    _attr_icon = "mdi:emoticon-outline"

    def __init__(self, coordinator):
        super().__init__(coordinator, "expression")

    @property
    def current_option(self):
        return self.coordinator.expression

    async def async_select_option(self, option):
        await self.coordinator.async_set_expression(option)
