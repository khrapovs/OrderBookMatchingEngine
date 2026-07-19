from datetime import datetime
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from order_matching.api.app import app
from order_matching.api.utils import create_market


@pytest.fixture
def sim_client() -> Iterator[TestClient]:
    # Set up client with a real market for simulation testing
    app.state.traders_enabled = True
    app.state.market = create_market(seed=42)
    app.state.trades = []
    with TestClient(app) as c:
        yield c


def test_match_runs_simulation_ticks(sim_client: TestClient) -> None:
    # Initially the order book should be empty because we reset prepopulate
    book = sim_client.get("/orders").json()
    assert book["bids"] == {}
    assert book["offers"] == {}

    # Call match at t0. The noise traders should place their first orders since next_trade_time is None.
    t0 = datetime(2023, 1, 1, 10, 0, 0)
    response = sim_client.post("/match", json={"timestamp": t0.isoformat()})
    assert response.status_code == 200

    # Verify that the noise traders have now populated the book
    book = sim_client.get("/orders").json()
    assert len(book["bids"]) > 0 or len(book["offers"]) > 0


def test_reset_recreates_simulation(sim_client: TestClient) -> None:
    # 1. Trigger a step to populate
    t0 = datetime(2023, 1, 1, 10, 0, 0)
    sim_client.post("/match", json={"timestamp": t0.isoformat()})

    # 2. Reset the market simulation
    reset_response = sim_client.post("/reset", json={"seed": 100})
    assert reset_response.status_code == 200

    # 3. Verify book is empty immediately after reset
    book = sim_client.get("/orders").json()
    assert book["bids"] == {}
    assert book["offers"] == {}

    # 4. Trigger match again. It should step and place new orders based on the new seed.
    t1 = datetime(2023, 1, 1, 10, 0, 1)
    sim_client.post("/match", json={"timestamp": t1.isoformat()})
    book = sim_client.get("/orders").json()
    assert len(book["bids"]) > 0 or len(book["offers"]) > 0
