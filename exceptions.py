from model import Batch, OrderLine


class AllocationError(Exception):
    pass


class WrongSKUError(AllocationError):
    def __init__(self, batch: Batch, order_line: OrderLine):
        super().__init__()
        self._batch = batch
        self._order_line = order_line

    def __str__(self):
        return (
            f"Несоответствие единицы складского учета (SKU) "
            f"партии {self._batch} и заказа {self._order_line}."
        )



class NotEnoughQuantityAllocationError(AllocationError):

    def __init__(self, batch: Batch, order_line: OrderLine):
        super().__init__()
        self._batch = batch
        self._order_line = order_line

    def __str__(self):
        return (
            f"Недостаточно ед. товара в партии {self._batch} "
            f"для размещения заказа {self._order_line}."
        )


class NotAllocatedOrderLineError(AllocationError):

    def __init__(self, batch: Batch, order_line: OrderLine):
        super().__init__()
        self._batch = batch
        self._order_line = order_line

    def __str__(self):
        return (
            f"Заказ {self._order_line} еще не размещен "
            f"в партии {self._batch}."
        )


class AlreadyAllocatedOrderLineError(AllocationError):

    def __init__(self, batch: Batch, order_line: OrderLine):
        super().__init__()
        self._batch = batch
        self._order_line = order_line

    def __str__(self):
        return f"Заказ {self._order_line} уже размещен в партии {self._batch}."
