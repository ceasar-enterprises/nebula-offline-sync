"""Conflict-free merge engine (Phase 1).

Merges two stores so every committed fact survives and state converges.
Stage 1a ships the identity guard and the union base case, which makes
invariant I5 true. Counter (add-wins) and LWW resolution grow here next.
"""

from copy import deepcopy

from .store import LocalStore


def merge(store: LocalStore, other: LocalStore) -> LocalStore:
    """Union-merge `other` into `store`, returning `store`.

    Idempotent: if `other is store`, nothing happens. Otherwise every object
    entry present in `other` but absent from `store` is copied in. A node
    merged with itself therefore never changes state and cannot drift.
    """

    if store is other:
        return store

    target = store._objects
    for key, entry in other._objects.items():
        if key not in target:
            target[key] = deepcopy(entry)

    return store


__all__ = ["merge"]