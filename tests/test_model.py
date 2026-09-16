"""Tests pinning the public domain model contract (Phase 0).

The types must stay stable-stable for downstream implementers of the sync
protocol. These tests lock the shapes; merge semantics arrive in Phase 1.
"""

import dataclasses

import nebula_offline_sync as engine
from nebula_offline_sync.model import (
    Order,
    OrderItem,
    Outlet,
    ProductItem,
    Receivable,
    StockMovement,
    Transaction,
)


def test_public_objects_exported():
    for name in (
        "ProductItem",
        "StockMovement",
        "OrderItem",
        "Order",
        "Receivable",
        "Transaction",
        "Outlet",
        "Checkpoint",
    ):
        assert hasattr(engine, name), name


def test_product_item_has_batch_and_expiry():
    p = ProductItem(
        id="P1",
        name="Paracetamol 500mg",
        category="Pharmacy",
        base_price=1000.0,
        current_price=1200.0,
        cost=800.0,
        stock=24,
        batch_no="B2026-07",
        expiry_date="2027-06-30",
    )
    assert p.stock == 24
    assert p.batch_no == "B2026-07"
    assert p.expiry_date == "2027-06-30"


def test_order_holds_line_items_and_totals():
    items = [
        OrderItem(product_id="P1", product_name="Paracetamol", quantity=2, unit_price=1200.0, subtotal=2400.0),
        OrderItem(product_id="P2", product_name="Cough Syrup", quantity=1, unit_price=5000.0, subtotal=5000.0),
    ]
    o = Order(id="O1", customer_id="C9", items=items, total=7400.0, status="new", outlet="Kampala Branch")
    assert o.status == "new"
    assert sum(i.subtotal for i in o.items) == o.total == 7400.0
    assert o.outlet == "Kampala Branch"


def test_stock_movement_reasons_are_bounded():
    known = {"restock", "adjust", "damage", "sale", "count", "initial"}
    for reason in known:
        m = StockMovement(id="M1", product_id="P1", delta=5, reason=reason)
        assert m.delta == 5


def test_receivable_aging_fields():
    r = Receivable(
        id="R1",
        customer_name="Acme Shop",
        kind="invoice",
        reference="INV-0001",
        amount=100000.0,
        paid=40000.0,
        status="partial",
        due_date="2026-10-01",
    )
    assert r.amount - r.paid == 60000.0
    assert r.status == "partial"


def test_transaction_fraud_flag():
    t = Transaction(id="T1", amount=2000000.0, payment_method="momo", status="completed", fraud_flag=True)
    assert t.fraud_flag


def test_outlet_is_a_sync_node():
    o = Outlet(id="B2", name="Main Store")
    assert o.id == "B2"


def test_all_types_are_data_classes():
    for cls in (ProductItem, StockMovement, OrderItem, Order, Receivable, Transaction, Outlet):
        assert dataclasses.is_dataclass(cls), cls