"""Shared workflow vocabulary for Switchyard.

Centralizes workflow state strings, agent decision values, and loop defaults so
workflow and adapter code never scatter these literals.
"""

from __future__ import annotations

# Workflow states (written to run metadata).
STATE_CREATED = "created"
STATE_PACKET_CREATED = "packet_created"
STATE_CODEX_PLAN_CREATED = "codex_plan_created"
STATE_CLAUDE_PLAN_REVIEWED = "claude_plan_reviewed"
STATE_CODEX_PLAN_CRITIQUED = "codex_plan_critiqued"
STATE_PLAN_REVISION_REQUESTED = "plan_revision_requested"
STATE_PLAN_APPROVED = "plan_approved"
STATE_BLOCKED_FOR_USER = "blocked_for_user"
STATE_MAX_ROUNDS_REACHED = "max_rounds_reached"
STATE_FINAL_PLAN_CREATED = "final_plan_created"
STATE_BLOCKED_REPORT_CREATED = "blocked_report_created"
STATE_COMPLETED = "completed"
STATE_FAILED = "failed"

# Agent review/critique decisions.
DECISION_APPROVED = "approved"
DECISION_NEEDS_REVISION = "needs_revision"
DECISION_BLOCKED = "blocked"
DECISION_UNKNOWN = "unknown"

# Bounded planning loop default.
MAX_PLAN_REVIEW_ROUNDS = 3
