# ABOUTME: Checks that the streaq Lua library on the Redis server honours this streaq's convention.
# ABOUTME: Redis functions are server-global, so another project's streaq silently replaces them.
import time
from typing import TYPE_CHECKING

from vibetuner.logging import logger


if TYPE_CHECKING:
    from coredis import Redis


# The probe's own keys live under the project's prefix, well away from streaq's
# `streaq:<queue>:` namespace, and carry a TTL so a probe killed mid-run leaves
# nothing behind.
_PROBE_KEYS = "{prefix}lua-probe:{name}"
_PROBE_TTL = 60


async def promotes_delayed_tasks(client: "Redis[str]", prefix: str) -> bool:
    """Return whether the server's streaq library promotes a due delayed task.

    streaq registers its Lua helpers as Redis functions, which are global to a
    Redis server rather than scoped to a database or key prefix: every worker
    installs them with ``replace=True``, so the last worker to start owns the
    library every other project then calls. ``publish_delayed_tasks`` changed
    its keys and argv shape in streaq 7.2.0, and a library from either side of
    that change reports success while promoting nothing, which stops all
    delayed and cron work with no error anywhere. Promoting one sentinel task
    through dedicated keys is the only way to tell the two apart.
    """
    from coredis.exceptions import ResponseError
    from streaq.types import Streaq

    delayed_key = _PROBE_KEYS.format(prefix=prefix, name="delayed")
    stream_key = _PROBE_KEYS.format(prefix=prefix, name="stream")
    due = int(time.time() * 1000)
    try:
        await client.zadd(delayed_key, {"probe": due - 1000})
        await client.expire(delayed_key, _PROBE_TTL)
        await Streaq(client).publish_delayed_tasks(delayed_key, stream_key, due)
        await client.expire(stream_key, _PROBE_TTL)
        return await client.xlen(stream_key) == 1
    except ResponseError as exc:
        logger.error("streaq's Lua functions are missing from this Redis: {}", exc)
        return False
    finally:
        await client.delete([delayed_key, stream_key])
