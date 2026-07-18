from fastapi import APIRouter, Request
from loguru import logger

from order_matching.api.models.requests import ResetRequest
from order_matching.api.models.responses import ResetResponse
from order_matching.api.utils import prepopulate_engine
from order_matching.matching_engine import MatchingEngine

router = APIRouter()


@router.post("/reset")
def reset_engine(*, request: Request, payload: ResetRequest) -> ResetResponse:
    # Reinitialize engine in app state
    engine = MatchingEngine(seed=payload.seed)
    if payload.prepopulate:
        engine = prepopulate_engine(engine)
    request.app.state.engine = engine
    request.app.state.trades = []
    logger.debug(f"Matching engine reset successfully with seed: {payload.seed}, prepopulate: {payload.prepopulate}")
    return ResetResponse(message="Matching engine reset successfully")
