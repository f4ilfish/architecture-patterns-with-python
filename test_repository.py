# pylint: disable=protected-access
from sqlalchemy import text

from model import Batch, OrderLine
import repository


def test_repository_can_save_a_batch(session):
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text('''SELECT reference, sku, quantity, eta FROM "batches"''')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session):
    insert_stmt = text(
        '''INSERT INTO order_lines (sku, qty)  VALUES ("GENERIC-SOFA", 12)'''
    )
    session.execute(insert_stmt)
    [[order_line_id]] = session.execute(
        text('''SELECT id FROM order_lines WHERE sku=:sku'''),
        {"sku": "GENERIC-SOFA"},
    )
    return order_line_id


def insert_batch(session, reference):
    insert_stmt = text(
            '''INSERT INTO batches (reference, sku, quantity, eta) 
               VALUES (:reference, "GENERIC-SOFA", 100, null)'''
        )
    session.execute(insert_stmt, {"reference": reference})
    select_stmt = text(
        '''SELECT id FROM batches 
           WHERE reference=:reference AND sku=:sku'''
    )
    properties = {"reference": reference, "sku": "GENERIC-SOFA"}
    [[batch_id]] = session.execute(select_stmt, properties)
    return batch_id


def insert_allocation(session, order_line_id, batch_id):
    stmt = text(
        '''INSERT INTO allocations (order_line_id, batch_id)
           VALUES (:order_line_id, :batch_id)'''
    )
    properties = {"order_line_id": order_line_id, "batch_id": batch_id}
    session.execute(stmt, properties)


def test_repository_can_retrieve_a_batch_with_allocations(session):
    order_line_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, order_line_id, batch1_id)

    repo = repository.SqlRepository(session)
    retrieved = repo.get("batch1")

    expected = Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved.quantity == expected.quantity
    assert retrieved.allocations == {OrderLine(1, "GENERIC-SOFA", 12)}


def get_allocations(session, reference):
    stmt = text(
        '''SELECT allocations.id 
           FROM allocations
                    JOIN order_lines ON allocations.order_line_id = order_lines.id
                    JOIN batches ON allocations.batch_id = batches.id
           WHERE batches.reference = :reference'''
    )
    rows = list(session.execute(stmt, {"reference": reference}))
    return {row[0] for row in rows}


def test_updating_a_batch(session):
    order1 = OrderLine(1, "WEATHERED-BENCH", 10)
    order2 = OrderLine(2, "WEATHERED-BENCH", 20)
    batch = Batch("batch1", "WEATHERED-BENCH", 100, eta=None)
    batch.allocate(order1)

    repo = repository.SqlRepository(session)
    repo.add(batch)
    session.commit()

    batch.allocate(order2)
    repo.add(batch)
    session.commit()

    assert get_allocations(session, "batch1") == {"order1", "order2"}
