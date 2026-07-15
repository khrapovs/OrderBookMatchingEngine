from datetime import datetime

from fastapi import APIRouter, Request

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import domain_trade_to_response
from order_matching.api.models.responses import TradeHistoryResponse

router = APIRouter()


@router.get("/trades")
def get_trades(
    request: Request, _engine: MatchingEngineDep, from_timestamp: datetime | None = None
) -> TradeHistoryResponse:
    trades = request.app.state.trades
    if from_timestamp is not None:
        trades = [t for t in trades if t.timestamp >= from_timestamp]

    trades_res = [domain_trade_to_response(t) for t in trades]
    return TradeHistoryResponse(trades=trades_res)
