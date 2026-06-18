"""Tests for run metadata persistence."""

from __future__ import annotations

import json

from switchyard import metadata
from switchyard.artifacts import METADATA_FILENAME
from switchyard.constants import STATE_CREATED, STATE_PACKET_CREATED
from switchyard.run_context import create_run_context


def test_init_metadata_writes_created_record(tmp_path):
    run_context = create_run_context("Add a thing", tmp_path)

    record = metadata.init_metadata(run_context)

    assert record["state"] == STATE_CREATED
    assert record["review_rounds"] == 0
    assert record["repo"] == str(tmp_path)
    on_disk = json.loads(
        (run_context.run_folder / METADATA_FILENAME).read_text(encoding="utf-8")
    )
    assert on_disk == record


def test_set_state_updates_state_and_extra_fields(tmp_path):
    run_context = create_run_context("Add a thing", tmp_path)
    metadata.init_metadata(run_context)

    record = metadata.set_state(
        run_context.run_folder, STATE_PACKET_CREATED, decision="approved"
    )

    assert record["state"] == STATE_PACKET_CREATED
    assert record["decision"] == "approved"
    assert metadata.read_metadata(run_context.run_folder)["state"] == STATE_PACKET_CREATED
