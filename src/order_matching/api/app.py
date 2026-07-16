from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from order_matching import __version__
from order_matching.api.routes import router
from order_matching.matching_engine import MatchingEngine

app = FastAPI(
    title="Order Book Matching Engine API",
    description="REST API wrapping the Order Book Matching Engine",
    version=__version__,
)

# Initialize global state
app.state.engine = MatchingEngine()
app.state.trades = []

# Permissive CORS middleware for demo use
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


# 13.6 Global exception handler for unexpected 500 errors
@app.exception_handler(Exception)
def global_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})


# 13.7 Validation exception handler for Pydantic 422 errors
@app.exception_handler(RequestValidationError)
def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": exc.errors()})
