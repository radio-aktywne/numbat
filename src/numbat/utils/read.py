from collections.abc import Iterator


class ReadableIterator:
    """Iterator wrapper providing a read method."""

    def __init__(self, iterator: Iterator[bytes]) -> None:
        self._iterator = iterator
        self._buffer = b""

    def read(self, size: int | None = -1) -> bytes:
        """Read bytes from the iterator."""
        if size is None or size < 0:
            return b"".join(self._iterator)

        while len(self._buffer) < size:
            try:
                self._buffer += next(self._iterator)
            except StopIteration:
                break

        data, self._buffer = self._buffer[:size], self._buffer[size:]
        return data
