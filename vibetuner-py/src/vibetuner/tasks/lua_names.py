# ABOUTME: Loads streaq's Lua helpers under major-versioned names (library streaq_v7, functions streaq_v7_*).
# ABOUTME: Stopgap for tastyware/streaq#179, so mixed streaq versions on one Redis server stop clashing.
"""Versioned names for streaq's server-global Redis function library.

streaq registers its Lua helpers as one Redis function library named
``streaq``. Redis functions are global to a server, not scoped to a database
number, and every worker or frontend that enters ``async with worker:``
replaces the library with its own copy. streaq 7.2.0 changed the calling
convention of ``publish_task`` and ``publish_delayed_tasks``, so whichever
project started last breaks enqueueing and delayed or cron promotion for every
other project on the server running a different streaq.

tastyware/streaq#179 names the library ``streaq_v<major>`` and each function
``streaq_v<major>_<name>``. Until a release carries it, this module gives the
installed streaq exactly those names: a ``Streaq`` subclass whose wrappers call
the versioned functions and whose constructor renames the Lua code it is asked
to load, patched in wherever streaq builds the library. A shimmed project and
one on an upstream release with #179 share one library, while projects on an
unshimmed streaq keep their unversioned ``streaq`` library to themselves.

Delete this module, and its calls, once vibetuner's streaq lower bound is a
release that includes tastyware/streaq#179; ``use_versioned_names()`` is
already a no-op on such a release.
"""

import inspect
import re
from typing import Any

import streaq
import streaq.task
import streaq.types
import streaq.worker
from coredis.commands.function import wraps
from coredis.typing import StringT
from streaq.types import ReadStreamsCallback, Streaq

from vibetuner.logging import logger


UNVERSIONED_NAME = "streaq"
VERSIONED_NAME = f"streaq_v{streaq.VERSION.split('.')[0]}"

# Every function streaq.lua registers, with the options streaq's own stubs pass
# to coredis' ``wraps``. The function name is bound when ``wraps`` decorates a
# stub, so each one has to be wrapped again under its versioned name.
_FUNCTION_OPTIONS: dict[str, dict[str, Any]] = {
    "create_groups": {"verify_existence": False},
    "fail_dependents": {"verify_existence": False},
    "publish_delayed_tasks": {"verify_existence": False},
    "publish_task": {"verify_existence": False},
    "read_streams": {"callback": ReadStreamsCallback()},
    "update_dependents": {"verify_existence": False},
    "refresh_timeout": {"verify_existence": False},
    "schedule_cron_job": {"verify_existence": False},
}

# The modules that build ``Streaq`` instances, looked up at call time.
_PATCHED_MODULES = (streaq.types, streaq.worker, streaq.task)

_SHEBANG = re.compile(rf"\A(\s*#!lua name=){UNVERSIONED_NAME}\n")
_REGISTER = re.compile(r"redis\.register_function\('(\w+)'")


def versioned_code(code: str) -> str:
    """Rename the library and every function in streaq's Lua source."""
    renamed, shebangs = _SHEBANG.subn(rf"\g<1>{VERSIONED_NAME}\n", code, count=1)
    if shebangs != 1:
        raise RuntimeError(
            f"streaq's Lua library no longer starts with '#!lua name={UNVERSIONED_NAME}'"
        )
    functions = _REGISTER.findall(renamed)
    if sorted(functions) != sorted(_FUNCTION_OPTIONS):
        raise RuntimeError(
            f"streaq's Lua library registers {sorted(functions)}, "
            f"expected {sorted(_FUNCTION_OPTIONS)}"
        )
    return _REGISTER.sub(
        lambda match: f"redis.register_function('{VERSIONED_NAME}_{match[1]}'",
        renamed,
    )


def _versioned_library() -> type[Streaq]:
    """Build a ``Streaq`` subclass that loads and calls the versioned names."""
    wrapped = {
        name for name, attr in vars(Streaq).items() if hasattr(attr, "__wrapped__")
    }
    if wrapped != set(_FUNCTION_OPTIONS):
        raise RuntimeError(
            f"streaq's Streaq library wraps {sorted(wrapped)}, "
            f"expected {sorted(_FUNCTION_OPTIONS)}"
        )

    class VersionedStreaq(Streaq):
        NAME = VERSIONED_NAME

        def __init__(
            self,
            client: Any,
            name: StringT | None = None,
            code: str | None = None,
            replace: bool = False,
        ) -> None:
            super().__init__(
                client, name, versioned_code(code) if code else code, replace
            )

    for name, options in _FUNCTION_OPTIONS.items():
        stub = inspect.unwrap(getattr(Streaq, name))
        function_name = f"{VERSIONED_NAME}_{name}"
        setattr(
            VersionedStreaq, name, wraps(function_name=function_name, **options)(stub)
        )
    VersionedStreaq.__name__ = VersionedStreaq.__qualname__ = Streaq.__name__
    return VersionedStreaq


def use_versioned_names() -> None:
    """Make every ``Streaq`` library streaq builds use the versioned names.

    A no-op when the installed streaq already versions its names (upstream
    #179) or when it has already run. Raises when streaq's internals no longer
    look the way this shim expects, since quietly loading the unversioned
    library is the failure it exists to prevent.
    """
    if streaq.types.Streaq.NAME == VERSIONED_NAME:
        return
    if Streaq.NAME != UNVERSIONED_NAME:
        raise RuntimeError(
            f"streaq's Lua library is named {Streaq.NAME!r}, expected "
            f"{UNVERSIONED_NAME!r} or {VERSIONED_NAME!r}"
        )
    for module in _PATCHED_MODULES:
        if getattr(module, "Streaq", None) is not Streaq:
            raise RuntimeError(f"{module.__name__} no longer uses streaq.types.Streaq")

    versioned = _versioned_library()
    for module in _PATCHED_MODULES:
        setattr(module, "Streaq", versioned)  # noqa: B010
    logger.debug("streaq Lua library renamed to {}", VERSIONED_NAME)
