from __future__ import annotations

import asyncio
from typing import Coroutine

TASKS: dict[int, asyncio.Task] = {}


def queue_task(coro: Coroutine):
    task = asyncio.create_task(coro)
    task_id = id(task)
    TASKS[task_id] = task
    task.add_done_callback(lambda x: TASKS.pop(task_id))
