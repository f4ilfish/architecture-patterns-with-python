from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

from exceptions import (
    WrongSKUError,
    NotEnoughQuantityAllocationError, NotAllocatedOrderLineError,
    AlreadyAllocatedOrderLineError,
)

@dataclass(frozen=True)
class OrderLine:
    """
    Товарная позиция (строки)

    Attributes:
        order_id (str): Ссылка на заказ
        sku (str): Единица складского учета (stock-keeping unit)
        quantity (int): Количество
    """

    order_id: str
    sku: str
    quantity: int


class Batch:
    """
    Партия

    Attributes:
        reference (str): Ссылка
        sku (str): Единица складского учета (stock-keeping unit)
        quantity (int): Доступное количество
        eta (date): Предполагаемый срок прибытия (estimated arrival time)
    """

    def __init__(
        self,
        reference: str,
        sku: str,
        quantity: int,
        eta: Optional[date] = None
    ):
        self._reference = reference
        self._sku = sku
        self._purchased_quantity = quantity
        self._eta = eta

        self._allocated_order_lines: Set[OrderLine] = set()

    @property
    def allocated_quantity(self) -> int:
        return sum(ol.quantity for ol in self._allocated_order_lines)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, order_line: OrderLine) -> None:

        if self._sku != order_line.sku:
            raise WrongSKUError()

        if order_line in self._allocated_order_lines:
            raise AlreadyAllocatedOrderLineError()

        if self.available_quantity < order_line.quantity:
            raise NotEnoughQuantityAllocationError()

        self._allocated_order_lines.add(order_line)
        return

    def deallocate(self, order_line: OrderLine) -> None:

        if self._sku != order_line.sku:
            raise WrongSKUError()

        if order_line not in self._allocated_order_lines:
            raise NotAllocatedOrderLineError()

        self._allocated_order_lines.remove(order_line)
        return
