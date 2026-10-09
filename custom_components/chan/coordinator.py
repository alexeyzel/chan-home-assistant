"""Coordinate native ESPHome entities without accessing ESPHome internals."""

import asyncio
from time import monotonic

from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_ACTIVE_ENTITY,
    CONF_DEVICE_ID,
    CONF_EXPRESSION_ENTITY,
    CONF_PHASE_ENTITY,
    EXPRESSIONS,
    PHASES,
)
from .session import Session


class ChanCoordinator:
    """Firmware state is authoritative; commands are serialized."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self.session = Session(entry.data[CONF_DEVICE_ID])
        self.expression = "neutral"
        self._listeners = set()
        self._lock = asyncio.Lock()
        self._stopped = False

    def entity_id(self, key):
        """Follow HA entity renames using registry IDs stored at setup."""
        entity = er.async_get(self.hass).async_get(self.entry.data[key])
        if entity is not None:
            return entity.entity_id
        return self.entry.data[key]

    @callback
    def start(self):
        """Subscribe to state changes and registry renames until entry unload."""
        # All state changes are filtered against current registry IDs to survive renames.
        self.entry.async_on_unload(self.hass.bus.async_listen("state_changed", self._on_state))
        self.entry.async_on_unload(self.stop)
        self.refresh()

    @callback
    def stop(self):
        """Invalidate issued tools even if their caller retains an API instance."""
        self._stopped = True
        self.session.update(available=False, active=False, phase="sleep")
        self._listeners.clear()

    @callback
    def _on_state(self, event):
        if event.data.get("entity_id") in {
            self.entity_id(key)
            for key in (CONF_ACTIVE_ENTITY, CONF_EXPRESSION_ENTITY, CONF_PHASE_ENTITY)
        }:
            self.refresh()

    @callback
    def refresh(self):
        if self._stopped:
            return
        states = {
            key: self.hass.states.get(self.entity_id(key))
            for key in (CONF_ACTIVE_ENTITY, CONF_EXPRESSION_ENTITY, CONF_PHASE_ENTITY)
        }
        available = all(
            state is not None and state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)
            for state in states.values()
        )
        phase_state = states[CONF_PHASE_ENTITY]
        phase = phase_state.state if phase_state is not None else "sleep"
        available = available and phase in PHASES
        active = available and states[CONF_ACTIVE_ENTITY].state == STATE_ON
        self.session.update(available=available, active=active, phase=phase)
        expression = states[CONF_EXPRESSION_ENTITY]
        self.expression = expression.state if expression is not None else "neutral"
        for listener in tuple(self._listeners):
            listener()

    @callback
    def subscribe(self, listener):
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    async def async_set_active(self, active):
        async with self._lock:
            self.refresh()
            if not self.session.available:
                raise HomeAssistantError("Chan firmware is unavailable")
            await self.hass.services.async_call(
                "switch",
                "turn_on" if active else "turn_off",
                {"entity_id": self.entity_id(CONF_ACTIVE_ENTITY)},
                blocking=True,
            )

    async def async_set_expression(self, expression, lease=None):
        async with self._lock:
            self.refresh()
            if expression not in EXPRESSIONS:
                raise HomeAssistantError("Unsupported Chan expression")
            if not self.session.available or not self.session.active:
                raise HomeAssistantError("Chan is asleep or unavailable")
            if lease is not None and not self.session.valid(lease, monotonic()):
                raise HomeAssistantError("Expression belongs to an expired Chan turn")
            await self.hass.services.async_call(
                "select",
                "select_option",
                {"entity_id": self.entity_id(CONF_EXPRESSION_ENTITY), "option": expression},
                blocking=True,
            )
