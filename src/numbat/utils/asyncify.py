import asyncio
from collections.abc import AsyncGenerator as BaseAsyncGenerator
from collections.abc import Generator as BaseGenerator
from types import TracebackType
from typing import Any, overload, override


class Generator[YieldType, SendType](BaseAsyncGenerator[YieldType, SendType]):
    """Async generator that wraps a synchronous generator."""

    def __init__(self, generator: BaseGenerator[YieldType, SendType]) -> None:
        self.generator = generator

    @override
    async def asend(self, value: SendType, /) -> YieldType:
        class Sentinel:
            pass

        def wrap() -> YieldType | Sentinel:
            try:
                return self.generator.send(value)
            except StopIteration:
                return Sentinel()

        item = await asyncio.to_thread(wrap)

        if isinstance(item, Sentinel):
            raise StopAsyncIteration from None

        return item

    @overload
    async def athrow(
        self,
        typ: type[BaseException],
        val: BaseException | object = None,
        tb: TracebackType | None = None,
        /,
    ) -> YieldType: ...
    @overload
    async def athrow(
        self, typ: BaseException, val: None = None, tb: TracebackType | None = None, /
    ) -> YieldType: ...
    @override
    async def athrow(self, *args: Any, **kwargs: Any) -> YieldType:
        class Sentinel:
            pass

        def wrap() -> YieldType | Sentinel:
            try:
                return self.generator.throw(*args, **kwargs)
            except (GeneratorExit, StopIteration):
                return Sentinel()

        item = await asyncio.to_thread(wrap)

        if isinstance(item, Sentinel):
            raise StopAsyncIteration from None

        return item
