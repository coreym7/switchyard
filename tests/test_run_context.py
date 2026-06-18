"""Tests for Switchyard run context creation."""

from __future__ import annotations

from datetime import datetime
import re

import pytest

from switchyard.artifacts import RUNS_SUBDIR_NAME, SWITCHYARD_DIR_NAME
from switchyard.run_context import _build_run_id, _slugify, create_run_context


def test_build_run_id_uses_expected_format():
    now = datetime(2026, 5, 4, 13, 37)

    assert _build_run_id("Add a hello function", now) == (
        "2026-05-04-1337-add-a-hello-function"
    )


def test_slugify_plain_words():
    assert _slugify("Add a hello function") == "add-a-hello-function"


def test_slugify_punctuation_has_safe_shape():
    slug = _slugify("Fix bug #42!!!")

    assert re.fullmatch(r"[a-z0-9-]+", slug)
    assert not slug.startswith("-")
    assert not slug.endswith("-")


def test_slugify_caps_long_tasks_at_40_characters():
    assert len(_slugify("a" * 200)) <= 40


def test_slugify_only_punctuation_falls_back_to_task():
    assert _slugify("!!!") == "task"


def test_slugify_non_ascii_keeps_safe_shape():
    slug = _slugify("caf\u00e9 d\u00e9j\u00e0 vu")

    assert re.fullmatch(r"[a-z0-9-]+", slug)


def test_create_run_context_creates_run_folder_under_target_repo(tmp_path):
    now = datetime(2026, 5, 4, 13, 37)

    run_context = create_run_context("Add a hello function", tmp_path, now=now)

    assert run_context.run_id == "2026-05-04-1337-add-a-hello-function"
    assert run_context.target_repo == tmp_path
    assert run_context.run_folder == (
        tmp_path
        / SWITCHYARD_DIR_NAME
        / RUNS_SUBDIR_NAME
        / "2026-05-04-1337-add-a-hello-function"
    )
    assert run_context.run_folder.is_dir()


def test_create_run_context_raises_on_same_minute_collision(tmp_path):
    now = datetime(2026, 5, 4, 13, 37)
    create_run_context("Add a hello function", tmp_path, now=now)

    with pytest.raises(FileExistsError):
        create_run_context("Add a hello function", tmp_path, now=now)
