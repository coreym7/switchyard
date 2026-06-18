"""Decision extraction from agent review/critique artifacts.

Switchyard's bounded planning loop is driven by an explicit decision token that
each reviewing agent emits in a trailing ``## Decision`` section. This module
turns that free-text trailer into one of the canonical decision constants so the
workflow engine never inspects raw agent prose.
"""

from __future__ import annotations

import re

from switchyard.constants import (
    DECISION_APPROVED,
    DECISION_BLOCKED,
    DECISION_NEEDS_REVISION,
    DECISION_UNKNOWN,
)

# Order matters: ``needs_revision`` is checked before ``approved`` so a phrase
# like "not approved, needs revision" resolves to the stronger signal.
_DECISION_PATTERNS = (
    (DECISION_BLOCKED, re.compile(r"\bblocked\b", re.IGNORECASE)),
    (DECISION_NEEDS_REVISION, re.compile(r"needs[_\s]+revision", re.IGNORECASE)),
    (DECISION_APPROVED, re.compile(r"\bapproved\b", re.IGNORECASE)),
)

_DECISION_HEADING = re.compile(r"^#{1,6}\s*decision\b.*$", re.IGNORECASE | re.MULTILINE)


def parse_decision(review_text: str) -> str:
    """Return the canonical decision token from a review/critique artifact.

    Scans the text under the final ``## Decision`` heading for a recognized
    decision keyword. If no decision heading is present, the whole text is
    scanned as a fallback. Returns ``DECISION_UNKNOWN`` when nothing matches so
    the caller can stop for user review rather than guessing.
    """
    section = _decision_section(review_text)
    for decision, pattern in _DECISION_PATTERNS:
        if pattern.search(section):
            return decision
    return DECISION_UNKNOWN


def _decision_section(review_text: str) -> str:
    """Return the text under the last ``## Decision`` heading, or the whole text."""
    matches = list(_DECISION_HEADING.finditer(review_text))
    if not matches:
        return review_text
    return review_text[matches[-1].end():]
