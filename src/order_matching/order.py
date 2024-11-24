from dataclasses import dataclass, field
from datetime import datetime

from order_matching.execution import Execution
from order_matching.side import Side
from order_matching.status import Status


@dataclass(kw_only=True)
class Order:
    """Single order base storage class."""

    side: Side
    price: float
    size: float
    timestamp: datetime
    order_id: str
    trader_id: str
    execution: Execution
    expiration: datetime = datetime.max
    status: Status = Status.OPEN
    price_number_of_digits: int = 1

    def __post_init__(self) -> None:
        self.price = round(number=self.price, ndigits=self.price_number_of_digits)


@dataclass(kw_only=True)
class LimitOrder(Order):
    """Single limit order storage class."""

    execution: Execution = field(init=False, default=Execution.LIMIT)


@dataclass(kw_only=True)
class MarketOrder(Order):
    """Single market order storage class."""

    execution: Execution = field(init=False, default=Execution.MARKET)
    price: float = field(init=False)

    def __post_init__(self) -> None:
        self.price = 0 if self.side == Side.SELL else float("inf")
