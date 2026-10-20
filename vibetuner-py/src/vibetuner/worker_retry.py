# ABOUTME: Retry policy for the streaq worker's coredis Redis client.
# ABOUTME: Waits out a Redis LOADING reply with logged exponential backoff.
from coredis.exceptions import BusyLoadingError, ConnectionError as RedisConnectionError
from coredis.retry import (
    CompositeRetryPolicy,
    ConstantRetryPolicy,
    ExponentialBackoffRetryPolicy,
    RetryPolicy,
)

from vibetuner.logging import logger


LOADING_BASE_DELAY = 0.5
LOADING_MAX_DELAY = 5.0


class LoadingRetryPolicy(ExponentialBackoffRetryPolicy):
    """Backs off while Redis replies ``LOADING``, logging every wait."""

    def will_retry(self, exc: BaseException) -> bool:
        retry = super().will_retry(exc)
        if retry:
            logger.warning(
                "Redis is loading its dataset in memory; waiting to retry ({})", exc
            )
        return retry


def worker_retry_policy(loading_timeout: float) -> RetryPolicy:
    """Retry policy for the worker's coredis client.

    A Redis that restarts with a dataset to read answers ``LOADING`` until it
    has finished reading it. coredis raises that as ``BusyLoadingError``, and
    its default policy retries it only twice 10ms apart, so the worker exits
    and crash-loops for as long as Redis keeps loading. This policy waits out
    the load instead, backing off exponentially for up to
    ``loading_timeout`` seconds.

    The first policy of the pair restates coredis's default, which passing a
    policy of our own would otherwise drop. It covers plain connection and
    timeout errors (coredis raises a read timeout as the builtin
    ``TimeoutError``), which stay unretried beyond those two quick attempts: an
    unreachable Redis must still fail fast and let the process be restarted.
    ``BusyLoadingError`` matches both policies, and the composite waits for the
    longest of their delays, so a LOADING reply gets the backoff.
    """
    return CompositeRetryPolicy(
        ConstantRetryPolicy(
            (RedisConnectionError, TimeoutError), retries=2, delay=0.01
        ),
        LoadingRetryPolicy(
            (BusyLoadingError,),
            retries=None,
            deadline=loading_timeout,
            base_delay=LOADING_BASE_DELAY,
            max_delay=LOADING_MAX_DELAY,
            jitter=True,
        ),
    )
