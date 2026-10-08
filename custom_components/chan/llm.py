"""Expose Chan expressions alongside Assist home-control tools."""

from time import monotonic

import probatio as vol
from homeassistant.helpers import llm

from .const import DOMAIN, EXPRESSIONS


class ChanAPI(llm.API):
    """One API per robot; no tools for unrelated callers or inactive sessions."""

    def __init__(self, hass, coordinator):
        super().__init__(
            hass=hass, id=f"chan_{coordinator.entry.entry_id}", name="Chan expressions"
        )
        self.coordinator = coordinator

    async def async_get_api_instance(self, llm_context):
        self.coordinator.refresh()
        lease = self.coordinator.session.lease(llm_context.device_id, monotonic())
        return llm.APIInstance(
            api=self,
            llm_context=llm_context,
            api_prompt=(
                "You are Chan, a calm home robot. Speak Ukrainian. "
                "Use chan_set_expression sparingly when a response benefits from a facial "
                "expression. Use neutral for routine home commands, warm for support, "
                "happy for celebration, focused for explanations. Do not claim to measure "
                "the user's emotions. Do not call expressions for every sentence. "
                "Expressions expire automatically and do not authorize home actions."
                if lease
                else ""
            ),
            tools=[ExpressionTool(self.coordinator, lease)] if lease else [],
        )


class ExpressionTool(llm.Tool):
    """Only choose a face; physical motion is outside this test release."""

    name = "chan_set_expression"
    integration = DOMAIN
    description = "Choose Chan's facial expression for the current spoken response."
    parameters = vol.Schema({vol.Required("expression"): vol.In(EXPRESSIONS)})
    annotations = llm.ToolAnnotations(
        read_only=False, destructive=False, idempotent=True, open_world=False
    )

    def __init__(self, coordinator, lease):
        self.coordinator = coordinator
        self.lease = lease

    async def async_call(self, hass, tool_input, llm_context):
        args = self.parameters(tool_input.tool_args)
        if llm_context.device_id != self.lease.device_id:
            return llm.ToolResult(data={"error": "wrong_device"}, error=True)
        await self.coordinator.async_set_expression(args["expression"], self.lease)
        return llm.ToolResult(data={"expression": args["expression"]})
