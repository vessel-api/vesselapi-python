"""Tests for SyncIterator and AsyncIterator."""

from __future__ import annotations

import pytest

from vessel_api_python._iterator import AsyncIterator, SyncIterator


class TestSyncIterator:
    """Tests for the synchronous pagination iterator."""

    def test_single_page(self) -> None:
        """Iterator returns all items from a single page."""
        def fetch():
            return [1, 2, 3], None
        it = SyncIterator(fetch)
        assert list(it) == [1, 2, 3]

    def test_multiple_pages(self) -> None:
        """Iterator fetches across multiple pages."""
        pages = [([1, 2], "token1"), ([3, 4], "token2"), ([5], None)]
        page_idx = 0

        def fetch():
            nonlocal page_idx
            result = pages[page_idx]
            page_idx += 1
            return result

        it = SyncIterator(fetch)
        assert list(it) == [1, 2, 3, 4, 5]

    def test_empty_result(self) -> None:
        """Iterator handles empty result set."""
        def fetch():
            return [], None
        it = SyncIterator(fetch)
        assert list(it) == []

    def test_error_on_first_page(self) -> None:
        """Iterator propagates errors from first fetch."""
        def fetch():
            raise RuntimeError("API error")
        it = SyncIterator(fetch)
        with pytest.raises(RuntimeError, match="API error"):
            list(it)

    def test_error_on_subsequent_page(self) -> None:
        """Iterator propagates errors from subsequent fetches."""
        call_count = 0

        def fetch():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [1, 2], "token1"
            raise RuntimeError("page 2 error")

        it = SyncIterator(fetch)
        items = []
        with pytest.raises(RuntimeError, match="page 2 error"):
            for item in it:
                items.append(item)
        assert items == [1, 2]

    def test_collect(self) -> None:
        """collect() returns all items as a list."""
        def fetch():
            return [1, 2, 3], None
        it = SyncIterator(fetch)
        assert it.collect() == [1, 2, 3]

    def test_does_not_mutate_outer_state(self) -> None:
        """Iterator should not mutate state visible to the caller."""
        outer_token = "initial"

        def fetch():
            return [1], None

        it = SyncIterator(fetch)
        list(it)
        assert outer_token == "initial"


class TestAsyncIterator:
    """Tests for the asynchronous pagination iterator."""

    @pytest.mark.asyncio
    async def test_single_page(self) -> None:
        async def fetch():
            return [1, 2, 3], None
        it = AsyncIterator(fetch)
        result = await it.collect()
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_multiple_pages(self) -> None:
        pages = [([1, 2], "token1"), ([3, 4], None)]
        page_idx = 0

        async def fetch():
            nonlocal page_idx
            result = pages[page_idx]
            page_idx += 1
            return result

        it = AsyncIterator(fetch)
        result = await it.collect()
        assert result == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_empty_result(self) -> None:
        async def fetch():
            return [], None
        it = AsyncIterator(fetch)
        result = await it.collect()
        assert result == []

    @pytest.mark.asyncio
    async def test_async_for_loop(self) -> None:
        async def fetch():
            return ["a", "b"], None
        it = AsyncIterator(fetch)
        items = []
        async for item in it:
            items.append(item)
        assert items == ["a", "b"]

    @pytest.mark.asyncio
    async def test_error_propagation(self) -> None:
        async def fetch():
            raise RuntimeError("async error")
        it = AsyncIterator(fetch)
        with pytest.raises(RuntimeError, match="async error"):
            await it.collect()
