from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

from exceptions import (
    WrongSKUError,
    NotEnoughQuantityToAllocationError,
    NotYetAllocatedOrderLineError,
    AlreadyAllocatedOrderLineError,
)

@dataclass(unsafe_hash=True)
class OrderLine:
    """
    Заказ (товарная позиция)

    Attributes:
        oid (int): Идентификатор заказа
        sku (str): Единица складского учета (stock-keeping unit)
        quantity (int): Количество
    """

    oid: int
    sku: str
    quantity: int

    def __str__(self):
        return f"Заказ {self.oid} ({self.sku} {self.quantity} шт.)"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(order_id={self.oid}, sku={self.sku}, "
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
        :param quantity: Количество ед. товаров
        :param eta: Предполагаемый срок прибытия (estimated time arrival)
        """

        self._reference = reference
        self._sku = sku
        self._quantity = quantity
        self._eta = eta
        self._allocations: Set[OrderLine] = set()

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __str__(self):
        return (
            f"Партия {self.reference} ({self._sku}, "
            f"всего {self._quantity} ед., "
            f"размещено {self.allocated_quantity} ед., "
            f"доступно {self.available_quantity} ед., "
            f"предполагаемый срок прибытия {self.eta})"
        )

    def ___repr___(self):
        return (
            f"{self.__class__.__name__}(reference={self.reference}, "
            f"sku={self._sku}, purchased_quantity={self._quantity}, "
            f"eta={self.eta}, allocations={self._allocations})"
        )

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def eta(self) -> Optional[date]:
        return self._eta

    @property
    def allocations(self) -> Set[OrderLine]:
        return self._allocations

    @property
    def allocated_quantity(self) -> int:
        return sum(ol.quantity for ol in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._quantity - self.allocated_quantity

    def allocate(self, order_line: OrderLine) -> None:
        if self._sku != order_line.sku:
            raise WrongSKUError(
                self._reference,
                self._sku,
                order_line.oid,
                order_line.sku
            )

        if order_line in self._allocations:
            raise AlreadyAllocatedOrderLineError(
                self._reference,
                order_line.oid,
            )

        if self.available_quantity < order_line.quantity:
            raise NotEnoughQuantityToAllocationError(
                self._reference,
                self._quantity,
                order_line.oid,
                order_line.quantity,
            )

        self._allocations.add(order_line)
        return None

    def deallocate(self, order_line: OrderLine) -> None:
        if self._sku != order_line.sku:
            raise WrongSKUError(
                self._reference,
                self._sku,
                order_line.oid,
                order_line.sku
            )

        if order_line not in self._allocations:
            raise NotYetAllocatedOrderLineError(
                self._reference,
                order_line.oid,
            )

        self._allocations.remove(order_line)
        return
