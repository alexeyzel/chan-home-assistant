"""Actual voice state reported by firmware, not inferred model state."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from .const import PHASES
from .entity import ChanEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ChanPhaseSensor(entry.runtime_data)])


class ChanPhaseSensor(ChanEntity, SensorEntity):
    """Expose firmware voice phase."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(PHASES)

    def __init__(self, coordinator):
        super().__init__(coordinator, "phase")

    @property
    def native_value(self):
        return self.coordinator.session.phase
