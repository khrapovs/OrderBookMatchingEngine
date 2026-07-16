from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class SideStr(StrEnum):
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


OrderRequest = Annotated[LimitOrderRequest | MarketOrderRequest, Field(discriminator="order_type")]


class PlaceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    orders: Annotated[list[OrderRequest], Field(min_length=1)]


class MatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timestamp: datetime


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: int | None = None
