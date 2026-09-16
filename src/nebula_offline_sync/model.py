"""Public domain data types (contract for the engine).

These are the objects a shop actually works with: inventory items,
batches/expiry, stock movements, sales/receipts, debtors, and reconciliation
events. The types are the *contract*; the conflict-free merge semantics on top
of them are authored in later phases.

Only engine-level types live here. NEBULA product logic stays closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ProductItem:
    """A stock-keeping item with batch/expiry tracking."""

    id: str
    name: str
    category: str
    base_price: float
    current_price: float
    cost: float
    stock: int
    batch_no: Optional[str] = None
    expiry_date: Optional[str] = None  # ISO date


@dataclass
class StockMovement:
    """One append-only change to a product's stock ledger."""

    id: str
    product_id: str
    delta: int
    reason: str  # restock | adjust | damage | sale | count | initial
    note: str = ""
    balance_after: Optional[int] = None
    created_at: str = ""  # ISO timestamp


@dataclass
class OrderItem:
    """A line item inside an order."""

    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float = 0.0


@dataclass
class Order:
    """A sale created at the counter, possibly offline."""

    id: str
    customer_id: Optional[str] = None
    items: List[OrderItem] = field(default_factory=list)
    total: float = 0.0
    status: str = "new"  # new | paid | fulfilled | cancelled
    payment_method: str = ""
    outlet: str = ""
    shipping_address: str = ""
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Receivable:
    """A debt owed by a customer (direct or invoiced)."""

    id: str
    customer_id: Optional[str] = None
    customer_name: str = ""
    kind: str = ""  # invoice | credit | other
    reference: str = ""
    amount: float = 0.0
    paid: float = 0.0
    status: str = "open"  # open | partial | paid | overdue
    due_date: str = ""
    issued_date: str = ""
    paid_at: Optional[str] = None


@dataclass
class Transaction:
    """A money movement: payments and reconciliation events."""

    id: str
    customer_id: Optional[str] = None
    amount: float = 0.0
    product: str = ""
    category: str = ""
    payment_method: str = ""
    outlet: str = ""
    status: str = "completed"
    date: str = ""
    fraud_flag: bool = False
    fraud_reason: str = ""


@dataclass
class Outlet:
    """A branch/store — the identity of a sync node."""

    id: str
    name: str


@dataclass
class Checkpoint:
    """Tamper-evident marker of state at a point in sync history."""

    node_id: str
    sequence: int
    hash: str
    created_at: str = ""


__all__ = [
    "ProductItem",
    "StockMovement",
    "OrderItem",
    "Order",
    "Receivable",
    "Transaction",
    "Outlet",
    "Checkpoint",
]