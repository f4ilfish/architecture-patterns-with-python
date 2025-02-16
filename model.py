from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

from exceptions import (
    WrongSKUError,
    NotEnoughQuantityAllocationError,
    NotAllocatedOrderLineError,
    AlreadyAllocatedOrderLineError,
)

@dataclass(unsafe_hash=True)
class OrderLine:
    """
    Заказ (товарная позиция)

    Attributes:
        order_id (str): Идентификатор заказа
        sku (str): Единица складского учета (stock-keeping unit)
        quantity (int): Количество
    """

    order_id: str
    sku: str
    quantity: int

    def __str__(self):
        return f"Заказ {self.order_id} ({self.sku} {self.quantity} шт.)"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(order_id={self.order_id}, sku={self.sku}, "
            f"quantity={self.quantity})"
        )


class Batch:
    """ Партия """

    def __init__(
        self,
        reference: str,
        sku: str,
        quantity: int,
        eta: Optional[date] = None
    ):
        """
        :param reference: Ссылка
        :param sku: Единица складского учета (stock-keeping unit)
        :param quantity: Количество
        :param eta: Предполагаемый срок прибытия (estimated arrival time)
        """

        self._reference = reference
        self._sku = sku
        self._purchased_quantity = quantity
        self._eta = eta

        self._allocated_order_lines: Set[OrderLine] = set()

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __str__(self):
        return (
            f"Партия {self.reference} "
            f"({self._sku}, всего {self._purchased_quantity} ед., "
            f"доступно {self.available_quantity} ед., дата {self.eta})"
        )

    def ___repr___(self):
        return (
            f"{self.__class__.__name__}(reference={self.reference}, "
            f"sku={self._sku}, purchased_quantity={self._purchased_quantity}, "
            f"eta={self.eta}, "
            f"allocated_order_line={self._allocated_order_lines})"
        )

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def eta(self) -> Optional[date]:
        return self._eta

    @property
    def allocated_quantity(self) -> int:
        return sum(ol.quantity for ol in self._allocated_order_lines)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, order_line: OrderLine) -> None:

        if self._sku != order_line.sku:
            raise WrongSKUError(self, order_line)

        if order_line in self._allocated_order_lines:
            raise AlreadyAllocatedOrderLineError(self, order_line)

        if self.available_quantity < order_line.quantity:
            raise NotEnoughQuantityAllocationError(self, order_line)

        self._allocated_order_lines.add(order_line)
        return

    def deallocate(self, order_line: OrderLine) -> None:

        if self._sku != order_line.sku:
            raise WrongSKUError(self, order_line)

        if order_line not in self._allocated_order_lines:
            raise NotAllocatedOrderLineError(self, order_line)

        self._allocated_order_lines.remove(order_line)
        return
