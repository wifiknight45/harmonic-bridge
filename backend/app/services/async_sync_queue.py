"""
async_sync_queue.py
Asynchronous sync queue and rate-limiting middleware for harmonic-bridge.
"""

import asyncio
import logging
import random
from typing import Callable, Any, Optional

logger = logging.getLogger("harmonic_bridge.sync")

class RateLimitException(Exception):
    """Raised when an API returns HTTP 429 Too Many Requests."""
    def __init__(self, retry_after: Optional[float] = None):
        self.retry_after = retry_after
        super().__init__("Rate limit exceeded")


async def execute_with_backoff(
    func: Callable[..., Any],
    *args,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    **kwargs
) -> Any:
    """
    Executes an async API request using exponential backoff with Full Jitter.
    Respects explicit HTTP 429 'Retry-After' headers when available.
    """
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except RateLimitException as exc:
            if attempt == max_retries - 1:
                logger.error(f"Max retries ({max_retries}) reached for {func.__name__}.")
                raise

            # Use API-provided Retry-After value if present; otherwise, apply Full Jitter backoff
            if exc.retry_after is not None:
                delay = exc.retry_after
            else:
                exp_backoff = min(max_delay, base_delay * (2 ** attempt))
                delay = random.uniform(0, exp_backoff)  # Full Jitter strategy

            logger.warning(
                f"Rate limited on {func.__name__}. Retrying in {delay:.2f}s "
                f"(Attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(delay)
        except Exception as e:
            logger.error(f"Unhandlable exception during {func.__name__}: {str(e)}")
            raise


class PlatformSyncQueue:
    """
    Isolated worker queue managing API throughput and concurrency per platform.
    """

    def __init__(self, platform_name: str, max_concurrent: int = 5, requests_per_second: float = 10.0):
        self.platform_name = platform_name
        self.queue: asyncio.Queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limit_delay = 1.0 / requests_per_second
        self._workers: list[asyncio.Task] = []
        self._running = False

    async def enqueue(self, func: Callable[..., Any], *args, **kwargs):
        """Adds an API sync job to the platform queue."""
        await self.queue.put((func, args, kwargs))

    async def _worker_loop(self):
        while self._running:
            func, args, kwargs = await self.queue.get()
            async with self.semaphore:
                try:
                    await execute_with_backoff(func, *args, **kwargs)
                    await asyncio.sleep(self.rate_limit_delay)
                except Exception as err:
                    logger.error(f"[{self.platform_name}] Task processing failed: {err}")
                finally:
                    self.queue.task_done()

    def start(self, worker_count: int = 3):
        """Starts worker tasks for processing jobs in the background."""
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker_loop()) for _ in range(worker_count)
        ]

    async def stop(self):
        """Gracefully drains the queue and cancels background workers."""
        await self.queue.join()
        self._running = False
        for worker in self._workers:
            worker.cancel()
