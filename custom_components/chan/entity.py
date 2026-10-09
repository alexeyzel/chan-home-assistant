"""Shared entity lifecycle for Chan controls."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class ChanEntity(Entity):
    """Push updates from the firmware through the coordinator."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, key):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.entry.unique_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.unique_id)},
            name="Chan",
            manufacturer="M5Stack",
            model="StackChan (CoreS3)",
        )

    @property
    def available(self):
        return self.coordinator.session.available

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self.coordinator.subscribe(self.async_write_ha_state))
