from datetime import date, timedelta
from typing import Tuple, Optional

import pytest

from exceptions import (
    NotEnoughQuantityAllocationError,
    WrongSKUError,
    NotAllocatedOrderLineError,
    AlreadyAllocatedOrderLineError
)

from model import Batch, OrderLine
from service import allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, order_line = _make_equal_sku_line_and_batch("sku_1", 10, 2)
    batch.allocate(order_line)

    assert batch.available_quantity == 8


def test_can_allocate_if_available_greater_than_required():
    batch, order_line = _make_equal_sku_line_and_batch("sku_1", 10, 2)
    batch.allocate(order_line)

    assert batch.available_quantity == 8


def test_cannot_allocate_if_available_smaller_than_required():
    batch, order_line = _make_equal_sku_line_and_batch("sku_1", 2, 10)

    with pytest.raises(NotEnoughQuantityAllocationError):
        batch.allocate(order_line)
        assert batch.available_quantity == 2


def test_can_allocate_if_available_equal_to_required():
    batch, order_line = _make_equal_sku_line_and_batch("sku_1", 10, 10)
    batch.allocate(order_line)

    assert batch.available_quantity == 0


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch_1", "sku_1", 10)
    order_line = OrderLine("order_1", "wrond_sku", 10)

    with pytest.raises(WrongSKUError):
        batch.allocate(order_line)
        assert batch.available_quantity == 10


def test_deallocate():
    (
        batch,
        order_line,
    ) = _make_equal_sku_line_and_batch("sku_1", 10, 2)
    batch.allocate(order_line)
    batch.deallocate(order_line)

    assert batch.available_quantity == 10


def test_can_only_deallocate_allocated_lines():
    (
        batch,
        unallocated_order_line,
    ) = _make_equal_sku_line_and_batch("sku_1", 10, 2)

    with pytest.raises(NotAllocatedOrderLineError):
        batch.deallocate(unallocated_order_line)
        assert batch.available_quantity == 10


def test_allocation_is_idempotent():
    batch, order_line = _make_equal_sku_line_and_batch("sku_1", 10, 2)
    batch.allocate(order_line)

    with pytest.raises(AlreadyAllocatedOrderLineError):
        batch.allocate(order_line)
        assert batch.available_quantity == 8


def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch("warehouse_batch", "sku_1", 10)
    shipment_batch = Batch("shipment_batch", "sku_1", 10, tomorrow)
    order_line = OrderLine("order_1", "sku_1", 2)

    allocate(order_line, [warehouse_batch, shipment_batch])

    assert warehouse_batch.available_quantity == 8
    assert shipment_batch.available_quantity == 10


def test_prefers_earlier_batches():
    earliest_batch = Batch("earliest_batch", "sku_1", 10, today)
    medium_batch = Batch("medium_batch", "sku_1", 10, tomorrow)
    latest_batch = Batch("latest_batch", "sku_1", 10, later)
    order_line = OrderLine("order_1", "sku_1", 2)

    allocate(order_line, [earliest_batch, medium_batch, latest_batch])

    assert earliest_batch.available_quantity == 8
    assert medium_batch.available_quantity == 10
    assert latest_batch.available_quantity == 10


def test_returns_allocated_batch_ref():
    warehouse_batch = Batch("warehouse_batch", "sku_1", 10)
    shipment_batch = Batch("shipment_batch", "sku_1", 10, tomorrow)
    order_line = OrderLine("order_1", "sku_1", 2)

    allocation = allocate(order_line, [warehouse_batch, shipment_batch])

    assert allocation == warehouse_batch.reference


def _make_equal_sku_line_and_batch(
    sku: str,
    batch_qty: int,
    line_qty: int,
    batch_eta: Optional[date] = None,
) -> Tuple[Batch, OrderLine]:
    batch = Batch("batch_1", sku, batch_qty, batch_eta)
    order_line = OrderLine("order_1", sku, line_qty)
    return batch, order_line
