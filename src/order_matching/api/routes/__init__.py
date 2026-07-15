from fastapi import APIRouter

from order_matching.api.routes.cancel_order import router as cancel_order_router
from order_matching.api.routes.get_orders import router as get_orders_router
from order_matching.api.routes.get_trades import router as get_trades_router
from order_matching.api.routes.match import router as match_router
from order_matching.api.routes.place_orders import router as place_orders_router
from order_matching.api.routes.reset import router as reset_router
from order_matching.api.routes.summary import router as summary_router

router = APIRouter()
router.include_router(place_orders_router)
router.include_router(match_router)
router.include_router(get_orders_router)
router.include_router(get_trades_router)
router.include_router(cancel_order_router)
router.include_router(reset_router)
router.include_router(summary_router)
