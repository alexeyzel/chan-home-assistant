"""Exercise actual HA registries, service dispatch and LLM APIs without hardware."""

from types import SimpleNamespace

import probatio as vol
import pytest
import pytest_asyncio
from homeassistant.config_entries import ConfigEntries, ConfigEntry
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import llm

from custom_components.chan.config_flow import ChanConfigFlow
from custom_components.chan.const import (
    CONF_ACTIVE_ENTITY,
    CONF_DEVICE_ID,
    CONF_EXPRESSION_ENTITY,
    CONF_PHASE_ENTITY,
    EXPRESSIONS,
)
from custom_components.chan.coordinator import ChanCoordinator
from custom_components.chan.llm import ChanAPI


@pytest_asyncio.fixture
async def robot(tmp_path):
    hass = HomeAssistant(str(tmp_path))
    hass.config_entries = ConfigEntries(hass, {})
    firmware_entry = ConfigEntry(
        domain="esphome",
        data={},
        options={},
        title="Test ESPHome",
        source="user",
        unique_id="test",
        version=1,
        minor_version=1,
        discovery_keys={},
        subentries_data=None,
    )
    # Register a simulated firmware entry without attempting a network connection.
    hass.config_entries._entries[firmware_entry.entry_id] = firmware_entry
    dr.async_setup(hass)
    await dr.async_load(hass, load_empty=True)
    await er.async_load(hass, load_empty=True)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=firmware_entry.entry_id, identifiers={("esphome", "test_robot")}
    )
    registry = er.async_get(hass)
    callbacks = []
    entities = {}
    for key, domain, name in (
        (CONF_ACTIVE_ENTITY, "switch", "chan_active"),
        (CONF_EXPRESSION_ENTITY, "select", "chan_expression"),
        (CONF_PHASE_ENTITY, "sensor", "chan_phase"),
    ):
        entities[key] = registry.async_get_or_create(
            domain,
            "esphome",
            name,
            suggested_object_id=name,
            device_id=device.id,
            config_entry=firmware_entry,
        )
    entry = SimpleNamespace(
        data={**{key: value.id for key, value in entities.items()}, CONF_DEVICE_ID: device.id},
        entry_id="entry",
        unique_id="robot",
        async_on_unload=callbacks.append,
    )
    hass.states.async_set(entities[CONF_ACTIVE_ENTITY].entity_id, "on")
    hass.states.async_set(
        entities[CONF_EXPRESSION_ENTITY].entity_id, "neutral", {"options": list(EXPRESSIONS)}
    )
    hass.states.async_set(entities[CONF_PHASE_ENTITY].entity_id, "thinking")
    coordinator = ChanCoordinator(hass, entry)
    coordinator.start()
    calls = []

    async def select_option(call):
        calls.append(dict(call.data))
        hass.states.async_set(call.data["entity_id"], call.data["option"])

    async def turn_off(call):
        calls.append(dict(call.data))
        hass.states.async_set(call.data["entity_id"], "off")

    hass.services.async_register("select", "select_option", select_option)
    hass.services.async_register("switch", "turn_off", turn_off)
    yield hass, coordinator, entities, calls
    for cancel in callbacks:
        cancel()
    await hass.async_block_till_done()
    await hass.async_stop(force=True)


def context(device_id="robot"):
    return llm.LLMContext(
        platform="gemini_live",
        context=Context(),
        language="uk",
        assistant="conversation",
        device_id=device_id,
    )


async def test_llm_api_calls_real_ha_service(robot):
    hass, coordinator, entities, calls = robot
    api = await ChanAPI(hass, coordinator).async_get_api_instance(
        context(coordinator.session.device_id)
    )
    result = await api.async_call_tool(
        llm.ToolInput(tool_name="chan_set_expression", tool_args={"expression": "happy"})
    )
    assert not result.error
    assert calls == [{"entity_id": entities[CONF_EXPRESSION_ENTITY].entity_id, "option": "happy"}]


async def test_llm_api_hides_tools_from_browser(robot):
    hass, coordinator, _, _ = robot
    api = await ChanAPI(hass, coordinator).async_get_api_instance(context(None))
    assert api.tools == []
    assert api.api_prompt == ""


async def test_llm_tools_reject_invalid_expression(robot):
    hass, coordinator, _, calls = robot
    api = await ChanAPI(hass, coordinator).async_get_api_instance(
        context(coordinator.session.device_id)
    )
    with pytest.raises(vol.Invalid):
        await api.async_call_tool(
            llm.ToolInput(tool_name="chan_set_expression", tool_args={"expression": "arbitrary"})
        )
    assert calls == []


async def test_stopped_robot_rejects_already_issued_tool(robot):
    hass, coordinator, entities, calls = robot
    api = await ChanAPI(hass, coordinator).async_get_api_instance(
        context(coordinator.session.device_id)
    )
    hass.states.async_set(entities[CONF_ACTIVE_ENTITY].entity_id, "off")
    with pytest.raises(HomeAssistantError):
        await api.async_call_tool(
            llm.ToolInput(tool_name="chan_set_expression", tool_args={"expression": "happy"})
        )
    assert calls == []


async def test_expression_failure_does_not_publish_optimistic_success(robot):
    hass, coordinator, _, _ = robot

    async def fail(call):
        raise HomeAssistantError("device disconnected")

    hass.services.async_register("select", "select_option", fail)
    with pytest.raises(HomeAssistantError):
        await coordinator.async_set_expression("happy")
    assert coordinator.expression == "neutral"


async def test_entity_rename_keeps_binding(robot):
    hass, coordinator, entities, calls = robot
    old = entities[CONF_EXPRESSION_ENTITY].entity_id
    er.async_get(hass).async_update_entity(old, new_entity_id="select.renamed_face")
    hass.states.async_remove(old)
    hass.states.async_set("select.renamed_face", "neutral")
    await coordinator.async_set_expression("warm")
    assert calls[-1]["entity_id"] == "select.renamed_face"


async def test_disconnected_firmware_is_unavailable(robot):
    hass, coordinator, entities, _ = robot
    hass.states.async_set(entities[CONF_PHASE_ENTITY].entity_id, "unavailable")
    coordinator.refresh()
    assert not coordinator.session.available
    with pytest.raises(HomeAssistantError):
        await coordinator.async_set_active(False)


async def test_config_flow_rejects_mixed_devices(robot):
    hass, _, entities, _ = robot
    firmware_entry = hass.config_entries.async_entries("esphome")[0]
    other_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=firmware_entry.entry_id, identifiers={("esphome", "other_robot")}
    )
    er.async_get(hass).async_update_entity(
        entities[CONF_PHASE_ENTITY].entity_id, device_id=other_device.id
    )
    flow = ChanConfigFlow()
    flow.hass = hass
    result = await flow.async_step_user({key: value.entity_id for key, value in entities.items()})
    assert result["errors"] == {"base": "mixed_devices"}


async def test_unloaded_coordinator_rejects_retained_tool_instance(robot):
    hass, coordinator, _, calls = robot
    api = await ChanAPI(hass, coordinator).async_get_api_instance(
        context(coordinator.session.device_id)
    )
    coordinator.stop()
    with pytest.raises(HomeAssistantError):
        await api.async_call_tool(
            llm.ToolInput(tool_name="chan_set_expression", tool_args={"expression": "happy"})
        )
    assert calls == []


async def test_reactivation_does_not_revive_old_tool_instance(robot):
    hass, coordinator, entities, calls = robot
    api = await ChanAPI(hass, coordinator).async_get_api_instance(
        context(coordinator.session.device_id)
    )
    hass.states.async_set(entities[CONF_ACTIVE_ENTITY].entity_id, "off")
    coordinator.refresh()
    hass.states.async_set(entities[CONF_ACTIVE_ENTITY].entity_id, "on")
    coordinator.refresh()
    with pytest.raises(HomeAssistantError):
        await api.async_call_tool(
            llm.ToolInput(tool_name="chan_set_expression", tool_args={"expression": "warm"})
        )
    assert calls == []
