from fastapi import APIRouter

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.responses import SideStr, SummaryLevel

router = APIRouter()


@router.get("/summary")
def get_summary(engine: MatchingEngineDep) -> list[SummaryLevel]:
    records = engine.unprocessed_orders.summary().collect().to_dicts()
    summary_res = [
        SummaryLevel(side=SideStr(r["side"]), price=float(r["price"]), size=float(r["size"]), count=int(r["count"]))
        for r in records
    ]
    return summary_res
