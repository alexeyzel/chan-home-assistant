"""Test safety boundaries for model expression requests."""

import pytest

from custom_components.chan.session import Session


def active_session():
    session = Session("robot")
    session.update(available=True, active=True, phase="thinking")
    return session


@pytest.mark.parametrize("device", [None, "browser", "another_robot"])
def test_unrelated_callers_never_receive_expression_tools(device):
    assert active_session().lease(device, 10) is None


@pytest.mark.parametrize("phase", ["sleep", "idle", "error"])
def test_non_conversation_states_do_not_grant_tools(phase):
    session = active_session()
    session.update(available=True, active=True, phase=phase)
    assert session.lease("robot", 10) is None


def test_expression_lease_survives_thinking_to_speaking():
    session = active_session()
    lease = session.lease("robot", 10)
    session.update(available=True, active=True, phase="speaking")
    assert session.valid(lease, 11)


def test_late_expression_does_not_cross_sleep_and_reactivation():
    session = active_session()
    lease = session.lease("robot", 10)
    session.update(available=True, active=False, phase="sleep")
    session.update(available=True, active=True, phase="thinking")
    assert not session.valid(lease, 11)


def test_new_listening_turn_invalidates_previous_reply():
    session = active_session()
    lease = session.lease("robot", 10)
    session.update(available=True, active=True, phase="listening")
    assert not session.valid(lease, 11)


def test_disconnect_invalidates_tools_even_after_reconnection():
    session = active_session()
    lease = session.lease("robot", 10)
    session.update(available=False, active=False, phase="sleep")
    session.update(available=True, active=True, phase="thinking")
    assert not session.valid(lease, 11)


def test_expired_and_future_dated_tools_are_rejected():
    session = active_session()
    lease = session.lease("robot", 10)
    assert not session.valid(lease, 26)
    assert not session.valid(lease, 9)


def test_repeated_phase_updates_do_not_cancel_current_reply():
    session = active_session()
    lease = session.lease("robot", 10)
    session.update(available=True, active=True, phase="thinking")
    assert session.valid(lease, 11)
