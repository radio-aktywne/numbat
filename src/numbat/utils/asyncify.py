import asyncio
from collections.abc import AsyncIterator, Iterator


class Sentinel:
    """Sentinel class for iterator termination."""


async def iterator[T](it: Iterator[T]) -> AsyncIterator[T]:
    """Convert an iterator to an async iterator."""
    sentinel = Sentinel()

    while True:
        item = await asyncio.to_thread(next, it, sentinel)

        if isinstance(item, Sentinel):
            break

        yield item
