
class WrongSKUError(Exception):
    pass


class NotEnoughQuantityAllocationError(Exception):
    pass


class NotAllocatedOrderLineError(Exception):
    pass

class AlreadyAllocatedOrderLineError(Exception):
    pass