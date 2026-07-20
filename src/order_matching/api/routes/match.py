from typing import Annotated

from fastapi import APIRouter, Body, Request

from order_matching.api.models.converters import domain_trade_to_response, to_naive
from order_matching.api.models.requests import MatchRequest
from order_matching.api.models.responses import MatchResponse

router = APIRouter()


@router.post("/match")
def match_orders(
    *,
    request: Request,
    payload: Annotated[MatchRequest, Body(openapi_examples=MatchRequest.model_json_schema()["openapi_examples"])],
) -> MatchResponse:
    executed_trades = request.app.state.market.step(timestamp=to_naive(payload.timestamp))
    request.app.state.trades += executed_trades
    trades_res = [domain_trade_to_response(t) for t in executed_trades.trades]
    return MatchResponse(trades=trades_res)
