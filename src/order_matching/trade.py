from dataclasses import dataclass
from datetime import datetime

from order_matching.execution import Execution
from order_matching.side import Side


@dataclass(kw_only=True)
class Trade:
    """Single trade storage class."""

    side: Side
    price: float
    size: float
    incoming_order_id: str
    book_order_id: str
    execution: Execution
    trade_id: str
    timestamp: datetime
