from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class SideStr(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str
    trader_id: str
    side: SideStr
    size: float = Field(gt=0)
    timestamp: datetime
    expiration: datetime | None = None


class LimitOrderRequest(OrderBase):
    order_type: Literal["limit"] = "limit"
    price: float = Field(gt=0)


class MarketOrderRequest(OrderBase):
    order_type: Literal["market"] = "market"


OrderRequest = Annotated[Union[LimitOrderRequest, MarketOrderRequest], Field(discriminator="order_type")]


class PlaceOrdersRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    orders: list[OrderRequest]


class MatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timestamp: datetime


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: int | None = None
