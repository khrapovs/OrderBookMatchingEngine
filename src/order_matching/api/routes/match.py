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
    market = request.app.state.market
    executed_trades = market.step(timestamp=to_naive(payload.timestamp))

    # Accumulate trades in app state
    request.app.state.trades.extend(executed_trades)

    trades_res = [domain_trade_to_response(t) for t in executed_trades]
    return MatchResponse(trades=trades_res)
