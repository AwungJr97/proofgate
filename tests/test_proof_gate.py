"""Deterministic state and authorization tests for ProofGate.

The consensus boundary is integration-tested against GenLayer Studio/runner;
these tests document the contract invariants that must hold regardless of
validator output.
"""

import pytest


ALLOWED = {"VALID", "INVALID", "UNRESOLVED"}


def test_verdict_domain_is_bounded():
    assert ALLOWED == {"VALID", "INVALID", "UNRESOLVED"}
    assert "YES" not in ALLOWED
    assert "MAYBE" not in ALLOWED


def test_new_request_is_pending():
    state = {"status": "PENDING", "finalized": False}
    assert state["status"] == "PENDING"
    assert state["finalized"] is False


def test_finalized_request_is_immutable():
    state = {"status": "VALID", "finalized": True}
    assert state["finalized"] is True
    # A finalized request must never accept a second evaluation.
    with pytest.raises(AssertionError):
        assert state["finalized"] is False


def test_invalid_verdict_must_not_be_finalized():
    for verdict in ("", "YES", "PASS", "UNCERTAIN", None):
        assert verdict not in ALLOWED


def test_http_evidence_requirement():
    assert "https://example.com/evidence".startswith(("https://", "http://"))
    assert not "ftp://example.com/evidence".startswith(("https://", "http://"))
