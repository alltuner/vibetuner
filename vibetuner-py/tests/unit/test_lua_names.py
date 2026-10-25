# ABOUTME: Unit tests for the shim that gives streaq's Lua library major-versioned names.
# ABOUTME: Checks the names match tastyware/streaq#179, the version gate, and loud failure on drift.
# ruff: noqa: S101
import inspect
import re
from pathlib import Path

import coredis
import pytest
import streaq
import streaq.task
import streaq.types
import streaq.worker
from vibetuner.tasks import lua_names
from vibetuner.tasks.lua_names import (
    VERSIONED_NAME,
    use_versioned_names,
    versioned_code,
)


STREAQ_DIR = Path(inspect.getfile(streaq)).parent
# The names tastyware/streaq#179 gives streaq 7, which a shimmed project must
# share with projects on an upstream release that includes it.
UPSTREAM_FUNCTIONS = {
    "streaq_v7_create_groups",
    "streaq_v7_fail_dependents",
    "streaq_v7_publish_delayed_tasks",
    "streaq_v7_publish_task",
    "streaq_v7_read_streams",
    "streaq_v7_update_dependents",
    "streaq_v7_refresh_timeout",
    "streaq_v7_schedule_cron_job",
}


def _shipped_code() -> str:
    return (STREAQ_DIR / "lua" / "streaq.lua").read_text()


@pytest.fixture
def unshimmed(monkeypatch: pytest.MonkeyPatch) -> type[streaq.types.Streaq]:
    """Put streaq's own Streaq class back in every module the shim patches."""
    original = lua_names.Streaq
    for module in (streaq.types, streaq.worker, streaq.task):
        monkeypatch.setattr(module, "Streaq", original)
    return original


def test_installed_streaq_needs_the_shim() -> None:
    """Fails once streaq ships #179: then raise the lower bound and delete the shim."""
    assert lua_names.Streaq.NAME == "streaq"
    assert VERSIONED_NAME == "streaq_v7"


def test_versioned_code_matches_upstream_names() -> None:
    code = versioned_code(_shipped_code())

    assert code.startswith("#!lua name=streaq_v7\n")
    assert set(re.findall(r"register_function\('(\w+)'", code)) == UPSTREAM_FUNCTIONS


def test_versioned_code_rejects_an_unexpected_library_name() -> None:
    with pytest.raises(RuntimeError, match="no longer starts with"):
        versioned_code(_shipped_code().replace("name=streaq", "name=other", 1))


def test_versioned_code_rejects_an_unknown_function() -> None:
    code = _shipped_code() + "\nredis.register_function('new_helper', function() end)\n"

    with pytest.raises(RuntimeError, match="new_helper"):
        versioned_code(code)


def test_applies_to_every_module_that_builds_the_library(
    unshimmed: type[streaq.types.Streaq],
) -> None:
    use_versioned_names()

    versioned = streaq.types.Streaq
    assert versioned is not unshimmed
    assert versioned.NAME == "streaq_v7"
    assert streaq.worker.Streaq is versioned
    assert streaq.task.Streaq is versioned


def test_renames_the_code_it_is_asked_to_load(
    unshimmed: type[streaq.types.Streaq],
) -> None:
    use_versioned_names()

    client = coredis.Redis()
    library = streaq.types.Streaq(client, code=_shipped_code(), replace=True)

    assert library.name == "streaq_v7"
    assert library.code.startswith("#!lua name=streaq_v7\n")


def test_is_idempotent(unshimmed: type[streaq.types.Streaq]) -> None:
    use_versioned_names()
    versioned = streaq.types.Streaq

    use_versioned_names()

    assert streaq.types.Streaq is versioned
    assert streaq.worker.Streaq is versioned


def test_does_nothing_when_streaq_already_versions_its_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class UpstreamStreaq(lua_names.Streaq):
        NAME = "streaq_v7"

    worker_library, task_library = object(), object()
    monkeypatch.setattr(streaq.types, "Streaq", UpstreamStreaq)
    monkeypatch.setattr(streaq.worker, "Streaq", worker_library)
    monkeypatch.setattr(streaq.task, "Streaq", task_library)

    use_versioned_names()

    assert streaq.types.Streaq is UpstreamStreaq
    assert streaq.worker.Streaq is worker_library
    assert streaq.task.Streaq is task_library


def test_fails_when_a_module_no_longer_uses_the_library(
    unshimmed: type[streaq.types.Streaq], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delattr(streaq.task, "Streaq")

    with pytest.raises(RuntimeError, match="streaq.task"):
        use_versioned_names()

    assert streaq.worker.Streaq is unshimmed


def test_fails_on_an_unexpected_library_name(
    unshimmed: type[streaq.types.Streaq], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(unshimmed, "NAME", "streaq_next")

    with pytest.raises(RuntimeError, match="streaq_next"):
        use_versioned_names()


def test_fails_when_streaq_wraps_a_new_function(
    unshimmed: type[streaq.types.Streaq], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(unshimmed, "new_helper", unshimmed.publish_task, raising=False)

    with pytest.raises(RuntimeError, match="new_helper"):
        use_versioned_names()


def test_only_patched_modules_build_the_library() -> None:
    """A new call site in streaq would keep loading the unversioned library."""
    builders = {
        path.relative_to(STREAQ_DIR).as_posix()
        for path in STREAQ_DIR.rglob("*.py")
        if re.search(r"\bStreaq\(", path.read_text())
    }

    assert builders == {"types.py", "worker.py", "task.py"}


def test_vibetuner_worker_module_applies_the_shim() -> None:
    import vibetuner.tasks.worker  # noqa: F401

    assert streaq.worker.Streaq.NAME == "streaq_v7"
    assert streaq.task.Streaq.NAME == "streaq_v7"
