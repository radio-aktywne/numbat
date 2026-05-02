import asyncio
from collections.abc import AsyncIterator as BaseAsyncIterator
from collections.abc import Iterator as BaseIterator
from typing import override


class Iterator[T](BaseIterator[T]):
    """Iterator that wraps an async iterator."""

    def __init__(
        self,
        iterator: BaseAsyncIterator[T],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self.iterator = iterator
        self.loop = loop if loop is not None else asyncio.get_running_loop()

    @override
    def __next__(self) -> T:
        class Sentinel:
            pass

        async def wrap() -> T | Sentinel:
            try:
                return await anext(self.iterator)
            except StopAsyncIteration:
                return Sentinel()

        future = asyncio.run_coroutine_threadsafe(wrap(), self.loop)
        item = future.result()

        if isinstance(item, Sentinel):
            raise StopIteration from None

        return item
