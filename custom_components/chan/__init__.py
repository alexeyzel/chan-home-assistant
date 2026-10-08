"""Chan robot coordination inside Home Assistant."""

import logging

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm

from .const import PLATFORMS
from .coordinator import ChanCoordinator
from .llm import ChanAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry):
    """Load a robot and its device-scoped expression API."""
    coordinator = ChanCoordinator(hass, entry)
    entry.runtime_data = coordinator
    coordinator.start()
    entry.async_on_unload(llm.async_register_api(hass, ChanAPI(hass, coordinator)))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    """Unload entities; entry callbacks remove listeners and the LLM API."""
    if entry.runtime_data.session.available:
        try:
            await entry.runtime_data.async_set_active(False)
        except HomeAssistantError:
            _LOGGER.warning("Could not stop Chan during unload; check the device connection")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
