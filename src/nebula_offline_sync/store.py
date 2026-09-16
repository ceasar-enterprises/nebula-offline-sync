"""Local storage seam (Phase 0 scaffold for the Phase 1 conflict-free core).

The concrete SQLite-backed engine arrives in Phase 1 and is authored by the
applicant. This module defines the stable seam the rest of the package codes
against, and wires every lifecycle event into the opt-in telemetry ledger so
real usage is captured from the first day a store exists.

Not production storage yet — the actual merge semantics, checkpoint
hashing, and SQLite persistence are Phase 1 work.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from . import telemetry


class StoreError(Exception):
    """Raised on storage-level violations (duplicate, missing, concurrency)."""


class LocalStore:
    """In-memory store that satisfies the engine seam.

    Phase 0: capacity-limited, no persistence, no merge logic. Its job is to
    lock the API and the event hooks; Phase 1 replaces the internals with the
    durable, conflict-free engine.
    """

    def __init__(self, node_id: str = "default", capacity: int = 1000, data_dir: Optional[str] = None, telemetry_enabled: bool = False):
        self.node_id = node_id
        self.capacity = capacity
        self._objects: Dict[str, Dict[str, Any]] = {}
        self.sync_count = 0
        telemetry.record("store_created", node_id=node_id)
        self._telemetry_enabled = telemetry_enabled

    def put(self, kind: str, obj_id: str, payload: Dict[str, Any]) -> str:
        """Insert or replace one object of a given kind."""
        key = f"{kind}:{obj_id}"
        if key in self._objects:
            raise StoreError(f"duplicate object {key}; use update()")
        if len(self._objects) >= self.capacity:
            raise StoreError("store capacity exceeded (Phase 0 in-memory cap)")
        self._objects[key] = {"kind": kind, "id": obj_id, "payload": payload, "node": self.node_id, "seq": len(self._objects) + 1}
        return key

    def update(self, kind: str, obj_id: str, payload: Dict[str, Any]) -> str:
        key = f"{kind}:{obj_id}"
        if key not in self._objects:
            raise StoreError(f"unknown object {key}; use put()")
        self._objects[key]["payload"] = payload
        return key

    def get(self, kind: str, obj_id: str) -> Optional[Dict[str, Any]]:
        item = self._objects.get(f"{kind}:{obj_id}")
        return dict(item["payload"]) if item else None

    def all(self) -> List[Dict[str, Any]]:
        return [dict(v) for v in self._objects.values()]

    def count(self) -> int:
        return len(self._objects)

    def sync(self) -> int:
        """Phase 0 placeholder: the phase where deltas get reconciled.

        Fires the telemetry event that future merged state will turn into the
        wire `sync_completed` payload. Returns events recorded this call.
        """
        events = telemetry.record("sync_completed", node_id=self.node_id, objects=self.count()) or 0
        if self._telemetry_enabled:
            telemetry.report_async(enabled=True)
        self.sync_count += 1
        return self.sync_count


def dumps_snapshot(store: LocalStore) -> str:
    """Deterministic snapshot of a store for checkpointing/hashing later."""
    rows = []
    for key in sorted(store._objects):
        v = store._objects[key]
        rows.append([v["kind"], v["id"], json.dumps(v["payload"], sort_keys=True), v["node"], v["seq"]])
    return json.dumps(rows, sort_keys=True)


def fingerprint(store: LocalStore) -> str:
    """sha256 of the deterministic snapshot — the `state_hash` primitive.

    Deterministic across runs and machines given identical object sets, so
    two nodes that have converged produce the same fingerprint. This is the
    building block for the tamper-evident checkpoint chain (Phase 1).
    """
    return hashlib.sha256(dumps_snapshot(store).encode("utf-8")).hexdigest()


__all__ = ["LocalStore", "StoreError", "dumps_snapshot"]