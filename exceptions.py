
class AllocationError(Exception):
    pass


class WrongSKUError(AllocationError):
    def __init__(
        self,
        batch_reference: str,
        batch_sku: str,
        order_line_oid: int,
        order_line_sku: str
    ) -> None:
        super().__init__()
        self._batch_reference = batch_reference
        self._batch_sku = batch_sku
        self._order_line_oid = order_line_oid
        self._order_line_sku = order_line_sku

    def __str__(self):
        return (
            f"Несоответствие единицы складского учета (SKU). "
            f"В партии {self._batch_reference} SKU {self._batch_sku}. "
            f"В заказе {self._order_line_oid} SKU {self._order_line_sku}."
        )


class NotEnoughQuantityToAllocationError(AllocationError):
    def __init__(
        self,
        batch_reference: str,
        batch_available_quantity: int,
        order_line_oid: int,
        order_line_qty: int
    ) -> None:
        super().__init__()
        self._batch_reference = batch_reference
        self._batch_available_quantity = batch_available_quantity
        self._order_line_oid = order_line_oid
        self._order_line_qty = order_line_qty

    def __str__(self):
        return (
            f"Недостаточно ед. товара для размещения в партии. "
            f"В партии {self._batch_reference} доступно "
            f"{self._batch_available_quantity} ед. "
            f"В заказе {self._order_line_oid} "
            f"{self._order_line_qty} для размещения."
        )


class NotYetAllocatedOrderLineError(AllocationError):
    def __init__(
        self,
        batch_reference: str,
        order_line_oid: int,
    ) -> None:
        super().__init__()
        self._batch_reference = batch_reference
        self._order_line_oid = order_line_oid

    def __str__(self):
        return (
            f"Заказ {self._order_line_oid} еще не размещен "
            f"в партии {self._batch_reference}."
        )


class AlreadyAllocatedOrderLineError(AllocationError):
    def __init__(
        self,
        batch_reference: str,
        order_line_oid: int,
    ) -> None:
        super().__init__()
        self._batch_reference = batch_reference
        self._order_line_oid = order_line_oid

    def __str__(self):
        return (
            f"Заказ {self._order_line_oid} уже размещен "
            f"в партии {self._batch_reference}."
        )
