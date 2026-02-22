"""Pagination iterators for the Vessel API Python SDK."""

from __future__ import annotations

from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")

# A fetch function returns (items, next_token_or_None).
FetchFunc = Callable[[], tuple[list[T], Optional[str]]]


class SyncIterator(Generic[T]):
    """Lazy, sequential iterator over paginated API results (sync).

    Implements the ``__iter__``/``__next__`` protocol so it can be used
    directly in ``for`` loops.

    Example::

        for vessel in client.search.all_vessels(filter_name="tanker"):
            print(vessel.name)
    """

    def __init__(self, fetch: FetchFunc[T]) -> None:
        self._fetch = fetch
        self._items: list[T] = []
        self._index = 0
        self._done = False
        self._started = False

    def __iter__(self) -> SyncIterator[T]:
        return self

    def __next__(self) -> T:
        # Advance index if we've already yielded at least one item.
        if self._started:
            self._index += 1
        self._started = True

        # Return buffered item if available.
        if self._index < len(self._items):
            return self._items[self._index]

        # No more pages.
        if self._done:
            raise StopIteration

        # Fetch next page.
        items, next_token = self._fetch()
        self._items = items
        self._index = 0

        if not items:
            self._done = True
            raise StopIteration

        if not next_token:
            self._done = True

        return self._items[self._index]

    def collect(self) -> list[T]:
        """Consume the iterator and return all remaining items as a list."""
        return list(self)


class AsyncIterator(Generic[T]):
    """Lazy, sequential iterator over paginated API results (async).

    Implements the ``__aiter__``/``__anext__`` protocol for use in
    ``async for`` loops.

    Example::

        async for vessel in client.search.all_vessels(filter_name="tanker"):
            print(vessel.name)
    """

    def __init__(self, fetch: Callable[[], object]) -> None:
        # fetch is an async callable returning (items, next_token).
        self._fetch = fetch
        self._items: list[T] = []
        self._index = 0
        self._done = False
        self._started = False

    def __aiter__(self) -> AsyncIterator[T]:
        return self

    async def __anext__(self) -> T:
        if self._started:
            self._index += 1
        self._started = True

        if self._index < len(self._items):
            return self._items[self._index]

        if self._done:
            raise StopAsyncIteration

        items, next_token = await self._fetch()  # type: ignore[misc]
        self._items = items
        self._index = 0

        if not items:
            self._done = True
            raise StopAsyncIteration

        if not next_token:
            self._done = True

        return self._items[self._index]

    async def collect(self) -> list[T]:
        """Consume the iterator and return all remaining items as a list."""
        result: list[T] = []
        async for item in self:
            result.append(item)
        return result
