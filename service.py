from typing import List

from exceptions import AllocationError
from model import OrderLine, Batch


def allocate(order_line: OrderLine, batches: List[Batch]) -> str:
    prefer_batch = next(batch for batch in sorted(batches))

    try:
        prefer_batch.allocate(order_line)
    except AllocationError as e:
        raise AllocationError(e) from e

    return prefer_batch.reference
