from fastapi import APIRouter, Request

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import domain_trade_to_response, to_naive
from order_matching.api.models.requests import MatchRequest
from order_matching.api.models.responses import MatchResponse

router = APIRouter()


@router.post("/match")
def match_orders(*, request: Request, payload: MatchRequest, engine: MatchingEngineDep) -> MatchResponse:
    executed_trades = engine.match(timestamp=to_naive(payload.timestamp))

    # Accumulate trades in app state
    request.app.state.trades.extend(executed_trades.trades)

    trades_res = [domain_trade_to_response(t) for t in executed_trades.trades]
    return MatchResponse(trades=trades_res)
