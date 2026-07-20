from typing import Annotated

from fastapi import APIRouter, Body, Request
from loguru import logger

from order_matching.api.models.requests import ResetRequest
from order_matching.api.models.responses import ResetResponse
from order_matching.api.utils import create_market
from order_matching.executed_trades import ExecutedTrades

router = APIRouter()


@router.post("/reset")
def reset_engine(
    *,
    request: Request,
    payload: Annotated[ResetRequest, Body(openapi_examples=ResetRequest.model_json_schema()["openapi_examples"])],
) -> ResetResponse:
    request.app.state.market = create_market(seed=payload.seed)
    request.app.state.trades = ExecutedTrades()
    logger.debug(f"Market simulation reset successfully with seed: {payload.seed}")
    return ResetResponse(message="Market simulation reset successfully")
