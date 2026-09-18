"""
test_async_sync_queue.py
Unit tests for RateLimitException, execute_with_backoff, and PlatformSyncQueue.
"""

import asyncio
from unittest.mock import AsyncMock, patch
import pytest

from app.services.async_sync_queue import (
    PlatformSyncQueue,
    RateLimitException,
    execute_with_backoff,
)


def test_rate_limit_exception_init():
    exc_default = RateLimitException()
    assert exc_default.retry_after is None
    assert str(exc_default) == "Rate limit exceeded"

    exc_custom = RateLimitException(retry_after=5.5)
    assert exc_custom.retry_after == 5.5


@pytest.mark.asyncio
async def test_execute_with_backoff_success():
    mock_func = AsyncMock(return_value="success")

    result = await execute_with_backoff(mock_func, "arg1", key="value")

    assert result == "success"
    assert mock_func.call_count == 1
    mock_func.assert_called_once_with("arg1", key="value")


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_with_backoff_retry_then_succeed(mock_sleep):
    mock_func = AsyncMock(
        side_effect=[RateLimitException(), RateLimitException(), "ok"]
    )

    result = await execute_with_backoff(mock_func, max_retries=3, base_delay=1.0)

    assert result == "ok"
    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_with_backoff_respects_retry_after(mock_sleep):
    mock_func = AsyncMock(
        side_effect=[RateLimitException(retry_after=4.2), "ok"]
    )

    result = await execute_with_backoff(mock_func, max_retries=3)

    assert result == "ok"
    assert mock_func.call_count == 2
    mock_sleep.assert_called_once_with(4.2)


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_execute_with_backoff_max_retries_exceeded(mock_sleep):
    mock_func = AsyncMock(side_effect=RateLimitException())

    with pytest.raises(RateLimitException):
        await execute_with_backoff(mock_func, max_retries=3)

    assert mock_func.call_count == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_execute_with_backoff_unhandled_exception():
    mock_func = AsyncMock(side_effect=ValueError("Database error"))

    with pytest.raises(ValueError, match="Database error"):
        await execute_with_backoff(mock_func, max_retries=3)

    assert mock_func.call_count == 1


@pytest.mark.asyncio
async def test_platform_sync_queue_processing_and_drain():
    queue = PlatformSyncQueue(
        platform_name="spotify", max_concurrent=2, requests_per_second=100.0
    )
    mock_task = AsyncMock(return_value="done")

    await queue.enqueue(mock_task, "track_1")
    await queue.enqueue(mock_task, "track_2")

    queue.start(worker_count=2)
    await queue.stop()

    assert mock_task.call_count == 2
    mock_task.assert_any_call("track_1")
    mock_task.assert_any_call("track_2")
