from fastapi import APIRouter, Request
from loguru import logger

from order_matching.api.models.requests import ResetRequest
from order_matching.api.models.responses import ResetResponse
from order_matching.api.utils import create_market

router = APIRouter()


@router.post("/reset")
def reset_engine(*, request: Request, payload: ResetRequest) -> ResetResponse:
    # Reinitialize market and engine in app state
    traders_enabled = getattr(request.app.state, "traders_enabled", True)
    market = create_market(seed=payload.seed, traders=None if traders_enabled else [])
    request.app.state.market = market
    request.app.state.trades = []
    logger.debug(f"Market simulation reset successfully with seed: {payload.seed}")
    return ResetResponse(message="Market simulation reset successfully")
