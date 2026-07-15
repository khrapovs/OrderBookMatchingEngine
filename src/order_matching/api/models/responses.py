from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class SideStr(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class ExecutionStr(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class StatusStr(StrEnum):
    OPEN = "OPEN"
    CANCEL = "CANCEL"


class OrderResponse(BaseModel):
    side: SideStr
    price: float
    size: float
    timestamp: datetime
    order_id: str
    trader_id: str
    execution: ExecutionStr
    status: StatusStr
    expiration: datetime


class TradeResponse(BaseModel):
    side: SideStr
    price: float
    size: float
    incoming_order_id: str
    book_order_id: str
    execution: ExecutionStr
    trade_id: str
    timestamp: datetime


class PlaceOrdersResponse(BaseModel):
    message: str
    orders: list[OrderResponse]


class MatchResponse(BaseModel):
    trades: list[TradeResponse]


class OrderBookResponse(BaseModel):
    bids: dict[float, list[OrderResponse]]
    offers: dict[float, list[OrderResponse]]


class TradeHistoryResponse(BaseModel):
    trades: list[TradeResponse]


class CancelOrderResponse(BaseModel):
    message: str


class ResetResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str


class SummaryLevel(BaseModel):
    side: SideStr
    price: float
    size: float
    count: int
