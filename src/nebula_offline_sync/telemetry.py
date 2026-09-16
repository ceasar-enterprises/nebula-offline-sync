"""Opt-in, anonymous adoption telemetry.

Tracks whether anyone actually runs the engine — the signal that answers "is
anyone using this code?". Absolutely nothing leaves the machine unless the
embedding application opts in via an explicit flag (see `report`).

Design:
- a random install id is generated once and stored next to the app's data dir;
- significant lifecycle events are appended to a local JSONL ledger;
- `report_async` posts only *aggregate-count* events (install, sync count,
  version) to a configurable endpoint, strictly opt-in, no business data.

Defaults: reporting DISABLED. Enable by passing `enabled=True` and a `url`.
"""

from __future__ import annotations

import json
import os
import platform
import threading
import time
import uuid
from typing import Any, Dict, Optional
from urllib import request

_DEFAULT_ENDPOINT = "https://nebula-enterprises.example/api/telemetry"
_VERSION = "0.1.0"

_installed: "Optional[_Installer]" = None
_lock = threading.Lock()


class TelemetryError(Exception):
    """Raised when opt-in reporting is attempted without a base dir."""


def _default_data_dir() -> str:
    """Cross-platform user data dir (platformdirs-style, no dependency)."""
    home = os.path.expanduser("~")
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or home
        return os.path.join(base, "NebulaOfflineSync")
    return os.path.join(home, ".local", "share", "nebula-offline-sync")


class _Installer:
    """Local ledger of install identity + lifecycle events."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.identity_path = os.path.join(self.data_dir, "install.json")
        self.ledger_path = os.path.join(self.data_dir, "events.jsonl")
        self._install_id = self._load_or_create_id()
        self._counters: Dict[str, int] = {}
        self._load_ledger()

    def _load_or_create_id(self) -> str:
        if os.path.exists(self.identity_path):
            try:
                with open(self.identity_path, encoding="utf-8") as fh:
                    return json.load(fh)["install_id"]
            except (OSError, ValueError, KeyError):
                pass
        iid = uuid.uuid4().hex
        try:
            with open(self.identity_path, "w", encoding="utf-8") as fh:
                json.dump({"install_id": iid, "created_at": time.time()}, fh)
        except OSError:
            pass
        return iid

    def _load_ledger(self) -> None:
        if not os.path.exists(self.ledger_path):
            return
        try:
            with open(self.ledger_path, encoding="utf-8") as fh:
                for line in fh:
                    try:
                        item = json.loads(line)
                    except ValueError:
                        continue
                    self._counters[item["event"]] = self._counters.get(item["event"], 0) + 1
        except OSError:
            pass

    def record(self, event: str, **extra: Any) -> None:
        self._counters[event] = self._counters.get(event, 0) + 1
        row = {
            "ts": time.time(),
            "install_id": self._install_id,
            "event": event,
            **extra,
        }
        try:
            with open(self.ledger_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
        except OSError:
            pass

    def snapshot(self) -> Dict[str, Any]:
        return {
            "install_id": self._install_id,
            "version": _VERSION,
            "platform": platform.system(),
            "python": platform.python_version(),
            "events": dict(self._counters),
        }


def init(data_dir: Optional[str] = None) -> _Installer:
    """Initialise the local ledger. Safe to call more than once."""
    global _installed
    with _lock:
        if _installed is None:
            _installed = _Installer(data_dir or _default_data_dir())
        return _installed


def record(event: str, **extra: Any) -> None:
    """Append a lifecycle event locally (always-on, local-only). No network."""
    try:
        init().record(event, **extra)
    except Exception:
        pass


def report(
    enabled: bool = False,
    url: Optional[str] = None,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """Opt-in network ping: send only the aggregate snapshot (no business data).

    `enabled` must be set explicitly by the embedding application. Without it,
    this is a strict no-op. Returns the server reply or an empty dict.
    """
    if not enabled:
        return {}
    try:
        inst = init()
        payload = json.dumps(inst.snapshot()).encode("utf-8")
        req = request.Request(
            url or _DEFAULT_ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": f"nebula-offline-sync/{_VERSION}"},
            method="POST",
        )
        with request.urlopen(req, timeout=timeout) as resp:
            return {"status": resp.status}
    except Exception as exc:
        return {"error": str(exc)}


def report_async(
    enabled: bool = False,
    url: Optional[str] = None,
    timeout: float = 5.0,
) -> None:
    """Fire-and-forget variant of `report` (never blocks the caller)."""
    t = threading.Thread(target=report, kwargs={"enabled": enabled, "url": url, "timeout": timeout}, daemon=True)
    t.start()


def install_id() -> str:
    try:
        return init()._install_id
    except Exception:
        return ""


__all__ = ["init", "record", "report", "report_async", "install_id"]