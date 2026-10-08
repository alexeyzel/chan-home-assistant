"""Conversation activation through the firmware's native switch."""

from homeassistant.components.switch import SwitchEntity

from .entity import ChanEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ChanConversationSwitch(entry.runtime_data)])


class ChanConversationSwitch(ChanEntity, SwitchEntity):
    """Start or stop the robot's Assist interaction."""

    _attr_icon = "mdi:robot"

    def __init__(self, coordinator):
        super().__init__(coordinator, "conversation")

    @property
    def is_on(self):
        return self.coordinator.session.active

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_set_active(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_set_active(False)
