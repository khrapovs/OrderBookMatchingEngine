from datetime import datetime

from fastapi import APIRouter, Request
from loguru import logger

from order_matching.api.models.converters import domain_trade_to_response, to_naive
from order_matching.api.models.responses import TradeHistoryResponse
from order_matching.executed_trades import ExecutedTrades

router = APIRouter()


@router.get("/trades")
def get_trades(*, request: Request, from_timestamp: datetime | None = None) -> TradeHistoryResponse:
    trades: ExecutedTrades = request.app.state.trades
    if from_timestamp is not None:
        trades = ExecutedTrades([t for t in trades.trades if t.timestamp >= to_naive(from_timestamp)])
    trades_res = [domain_trade_to_response(t) for t in trades]
    logger.debug(f"Produced trade history with {len(trades_res)} trades since {from_timestamp}")
    return TradeHistoryResponse(trades=trades_res)
