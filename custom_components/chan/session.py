"""Small, HA-independent guard for expression requests.

Identity, persistent memory and physical motion are deliberately outside v0.1.
"""

from dataclasses import dataclass

from .const import TOOL_MAX_AGE


@dataclass(frozen=True)
class ExpressionLease:
    """Bind a tool to a device, activation and listening turn."""

    device_id: str
    generation: int
    issued_at: float


@dataclass
class Session:
    """Invalidate old tools on sleep, disconnection or a new listening turn."""

    device_id: str
    available: bool = False
    active: bool = False
    phase: str = "sleep"
    generation: int = 0

    def update(self, *, available: bool, active: bool, phase: str) -> None:
        """Track authoritative firmware state without assuming commands succeeded."""
        if (
            available != self.available
            or active != self.active
            or (phase == "listening" and phase != self.phase)
        ):
            self.generation += 1
        self.available = available
        self.active = active
        self.phase = phase

    def lease(self, device_id: str | None, now: float) -> ExpressionLease | None:
        """Do not grant tools to browser calls or unrelated satellites."""
        if device_id != self.device_id or not self.available or not self.active:
            return None
        if self.phase not in ("listening", "thinking", "speaking"):
            return None
        return ExpressionLease(self.device_id, self.generation, now)

    def valid(self, lease: ExpressionLease, now: float) -> bool:
        """Reject late calls and requests from completed or cancelled turns."""
        return (
            self.available
            and self.active
            and self.phase in ("listening", "thinking", "speaking")
            and lease.device_id == self.device_id
            and lease.generation == self.generation
            and 0 <= now - lease.issued_at <= TOOL_MAX_AGE
        )
