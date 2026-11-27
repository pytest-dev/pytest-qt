from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING or hasattr(pytest, "StashKey"):
    from pytest import StashKey as StashKey
else:
    from _pytest.store import StoreKey

    StashKey = StoreKey


def _get_item_stash(item: pytest.Item) -> pytest.Stash:
    """Return the item's storage, using its equivalent Store on pytest 6.2."""
    if TYPE_CHECKING or hasattr(item, "stash"):
        return item.stash
    return item._store


def get_marker(item: pytest.Item, name: str) -> pytest.Mark | None:
    """Get a marker from a pytest item.

    This is here in order to stay compatible with pytest < 3.6 and not produce
    any deprecation warnings with >= 3.6.
    """
    try:
        return item.get_closest_marker(name)
    except AttributeError:
        # pytest < 3.6
        return item.get_marker(name)  # type: ignore[attr-defined,no-any-return]
