from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReviewQueueStore:
    _items: list[dict] = field(default_factory=list)

    def enqueue(self, item: dict) -> dict:
        self._items.append(item)
        return item

    def list_items(self) -> list[dict]:
        return self._items[:]


review_queue_store = ReviewQueueStore()
