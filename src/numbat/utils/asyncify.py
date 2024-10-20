import asyncio
from collections.abc import AsyncIterator, Iterator


async def iterator[T](it: Iterator[T]) -> AsyncIterator[T]:
    """Convert an iterator to an async iterator."""

    sentinel = object()

    while True:
        item = await asyncio.to_thread(next, it, sentinel)

        if item is sentinel:
            break

        yield item
