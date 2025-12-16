"""Async-to-sync bridge utilities for Typer CLI."""

import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")


def run_async(
    async_func: Callable[..., Coroutine[Any, Any, T]],
) -> Callable[..., T]:
    """Decorator that runs an async function synchronously.

    Used to bridge Typer (sync) with async database operations.

    Args:
        async_func: An async function to wrap.

    Returns:
        A synchronous wrapper function.
    """

    @wraps(async_func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return asyncio.run(async_func(*args, **kwargs))

    return wrapper
