"""Tests for review/critique decision extraction."""

from __future__ import annotations

from switchyard.constants import (
    DECISION_APPROVED,
    DECISION_BLOCKED,
    DECISION_NEEDS_REVISION,
    DECISION_UNKNOWN,
)
from switchyard.decision import parse_decision


def test_parse_decision_reads_approved_from_decision_section():
    text = "# Review\n\nLooks good.\n\n## Decision\n\napproved\n\nReason: scoped."
    assert parse_decision(text) == DECISION_APPROVED


def test_parse_decision_reads_needs_revision_with_space_or_underscore():
    assert parse_decision("## Decision\nneeds_revision\nreason") == DECISION_NEEDS_REVISION
    assert parse_decision("## Decision\nneeds revision\nreason") == DECISION_NEEDS_REVISION


def test_parse_decision_reads_blocked():
    assert parse_decision("## Decision\nblocked\nambiguous") == DECISION_BLOCKED


def test_parse_decision_prefers_blocked_then_needs_revision_over_approved():
    text = "## Decision\nnot approved, this is blocked and needs revision"
    assert parse_decision(text) == DECISION_BLOCKED
    text2 = "## Decision\nnot approved yet, needs revision"
    assert parse_decision(text2) == DECISION_NEEDS_REVISION


def test_parse_decision_only_scans_below_last_decision_heading():
    text = "approved earlier in prose\n\n## Decision\n\nblocked"
    assert parse_decision(text) == DECISION_BLOCKED


def test_parse_decision_falls_back_to_whole_text_without_heading():
    assert parse_decision("Everything is approved here.") == DECISION_APPROVED


def test_parse_decision_returns_unknown_when_no_keyword():
    assert parse_decision("## Decision\n\nlooks fine to me") == DECISION_UNKNOWN
