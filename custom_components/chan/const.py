"""Constants for the first Chan hardware/Assist test."""

DOMAIN = "chan"
CONF_ACTIVE_ENTITY = "active_entity"
CONF_EXPRESSION_ENTITY = "expression_entity"
CONF_PHASE_ENTITY = "phase_entity"
CONF_DEVICE_ID = "device_id"
EXPRESSIONS = ("neutral", "warm", "happy", "sad", "surprised", "focused")
PHASES = ("sleep", "idle", "listening", "thinking", "speaking", "error")
TOOL_MAX_AGE = 15.0
PLATFORMS = ("switch", "select", "sensor")
