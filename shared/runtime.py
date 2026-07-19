"""Runtime safety helpers shared by keel hooks and background jobs."""
from __future__ import annotations

import fcntl
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from shared.store import root

INTERNAL_LLM_ENV = "KEEL_INTERNAL_LLM"


def is_internal_llm() -> bool:
    """True inside a Claude subprocess launched by keel itself."""
    return os.environ.get(INTERNAL_LLM_ENV) == "1"


@contextmanager
def try_lock(name: str) -> Iterator[bool]:
    """Acquire a machine-wide non-blocking lock for the lifetime of the context."""
    lock_dir = root() / "runtime"
    lock_dir.mkdir(parents=True, exist_ok=True)
    path = lock_dir / f"{name}.lock"
    with path.open("a+") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        try:
            handle.seek(0)
            handle.truncate()
            handle.write(str(os.getpid()))
            handle.flush()
            yield True
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
