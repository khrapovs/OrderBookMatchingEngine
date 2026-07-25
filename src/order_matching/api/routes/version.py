from fastapi import APIRouter

from order_matching import __version__
from order_matching.api.models.responses import VersionResponse

router = APIRouter()


@router.get("/version")
def get_version() -> VersionResponse:
    return VersionResponse(version=__version__)
