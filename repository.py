import abc

from sqlalchemy import text
from sqlalchemy.orm import Session
from model import Batch


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, batch: Batch) -> None:

        self.session.add(batch)
        self.session.commit()

        # stmt = text(
        #     "INSERT INTO batches (reference, sku, quantity, eta) "
        #     "VALUES (:reference, :sku, :quantity, :eta)"
        # )
        # self.session.execute(
        #     stmt,
        #     {
        #         "reference": batch.reference,
        #         "sku": batch.sku,
        #         "quantity": batch.quantity,
        #         "eta": batch.eta,
        #     },
        # )
        # if batch.allocations:
        #     stmt = text(
        #         '''INSERT INTO order_lines (sku, quantity)
        #            VALUES (:sku, :quantity)'''
        #     )
        #     for order_line in batch.allocations:
        #         self.session.execute(
        #             stmt,
        #             {"sku": order_line.sku, "quantity": order_line.quantity},
        #         )
        return None

    def get(self, reference) -> Batch | None:
        stmt = text("SELECT * FROM batches WHERE reference = :reference")
        row = self.session.execute(stmt, {"reference": reference}).mappings().first()
        if row is not None:
            return Batch(
                reference=row["reference"],
                sku=row["sku"],
                quantity=row["quantity"],
                eta=row["eta"],
            )
        return None
