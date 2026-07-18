from collections.abc import Iterator
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from order_matching.api.app import app
from order_matching.matching_engine import MatchingEngine
from order_matching.simulation.market import Market
from order_matching.simulation.news_feed import NewsFeed


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Reset application state for each test to guarantee isolation
    app.state.traders_enabled = False
    app.state.market = Market(traders=[], news_feed=NewsFeed())
    app.state.engine = app.state.market.engine
    app.state.trades = []
    with TestClient(app) as c:
        yield c


@pytest.fixture
def reset_engine(_client: TestClient) -> MatchingEngine:
    app.state.traders_enabled = False
    app.state.market = Market(traders=[], news_feed=NewsFeed())
    app.state.engine = app.state.market.engine
    app.state.trades = []
    return app.state.engine


@pytest.fixture
def sample_timestamp() -> datetime:
    return datetime(2023, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_limit_order(sample_timestamp: datetime) -> dict[str, Any]:
    return {
        "order_type": "limit",
        "order_id": "order1",
        "trader_id": "trader1",
        "side": "BUY",
        "size": 10.0,
        "price": 100.0,
        "timestamp": sample_timestamp.isoformat(),
    }


@pytest.fixture
def sample_market_order(sample_timestamp: datetime) -> dict[str, Any]:
    return {
        "order_type": "market",
        "order_id": "order2",
        "trader_id": "trader2",
        "side": "SELL",
        "size": 5.0,
        "timestamp": sample_timestamp.isoformat(),
    }
