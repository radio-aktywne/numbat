import asyncio
from collections.abc import AsyncIterator, Generator, Iterator


class Sentinel:
    """Sentinel class for iterator termination."""


def iterator[T](
    it: AsyncIterator[T], loop: asyncio.AbstractEventLoop | None = None
) -> Iterator[T]:
    """Convert an async iterator to an iterator."""

    def _iterate(it: AsyncIterator[T], loop: asyncio.AbstractEventLoop) -> Generator[T]:
        sentinel = Sentinel()

        while True:
            coroutine = anext(it, sentinel)
            future = asyncio.run_coroutine_threadsafe(coroutine, loop)
            item = future.result()

            if isinstance(item, Sentinel):
                break

            yield item

    loop = loop if loop is not None else asyncio.get_running_loop()
    return _iterate(it, loop)
