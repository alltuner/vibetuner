---
paths:
  - src/*/tasks/**
description: Background tasks, cron jobs, robust_task, and robust_cron patterns
---

# Background Tasks

```python
from vibetuner.tasks.worker import get_worker
worker = get_worker()

@worker.task()
async def send_digest_email(user_id: str): ...
```

List in `tune.py` `tasks=[]`. Queue with
`await send_digest_email.enqueue(user.id)`.

**Robust tasks** (retries + dead letters):
`from vibetuner.tasks.robust import robust_task, robust_cron`.
`@robust_task(max_retries=3)` for enqueued tasks.
`@robust_cron("*/15 * * * *", max_retries=3)` for scheduled tasks.
Both support `backoff_base`, `backoff_max`, `timeout`, `on_failure`
callback. Failed tasks stored in `dead_letters` MongoDB collection.

**Cron** (no retries): `@worker.cron("0 9 * * *")`.
