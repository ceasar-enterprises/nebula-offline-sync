"""NEBULA Offline Sync Engine.

Local-first storage and conflict-free sync for business applications that run
where the internet doesn't.

Extracted and matured from the NEBULA business platform (proprietary). Only the
engine core lives here; product logic stays closed.
"""

from .model import (
    Checkpoint,
    Order,
    OrderItem,
    Outlet,
    ProductItem,
    Receivable,
    StockMovement,
    Transaction,
)
from .telemetry import install_id, record, report, report_async

__all__ = [
    "Checkpoint",
    "Order",
    "OrderItem",
    "Outlet",
    "ProductItem",
    "Receivable",
    "StockMovement",
    "Transaction",
    "install_id",
    "record",
    "report",
    "report_async",
]

__version__ = "0.1.0"