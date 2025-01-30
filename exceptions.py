

class AllocationError(Exception):
    pass


class WrongSKUError(AllocationError):
    pass


class NotEnoughQuantityAllocationError(AllocationError):
    pass


class NotAllocatedOrderLineError(AllocationError):
    pass


class AlreadyAllocatedOrderLineError(AllocationError):
    pass
