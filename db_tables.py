from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import registry, relationship

from model import OrderLine, Batch


mapper_registry = registry()
metadata = mapper_registry.metadata


order_lines = Table(
    "order_lines",
    metadata,
Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
)

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("batch_id", ForeignKey("batches.id")),
    Column("order_line_id", ForeignKey("order_lines.id")),
)

mapper_registry.map_imperatively(
    Batch,
    batches,
    properties={
        "_reference": batches.c.reference,
        "_sku": batches.c.sku,
        "_quantity": batches.c.quantity,
        "_eta": batches.c.eta,
        "order_lines": relationship(
            OrderLine,
            secondary=allocations,
            back_populates="batches",
        ),
    },
)

mapper_registry.map_imperatively(
    OrderLine,
    order_lines,
    properties={
        "oid": order_lines.c.id,
        "batches": relationship(
            Batch,
            secondary=allocations,
            back_populates="order_lines",
        ),
    }
)
