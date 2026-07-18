from datetime import datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient


def test_get_empty_trade_history(client: TestClient) -> None:
    response = client.get("/trades")
    assert response.status_code == 200
    assert response.json()["trades"] == []


def test_get_trades_accumulation_and_filtering(
    client: TestClient, *, sample_timestamp: datetime, sample_limit_order: dict[str, Any]
) -> None:
    # Place buy at 100
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place crossing sell at 95 at T+1 second
    sell_order1 = sample_limit_order.copy()
    sell_order1["order_id"] = "sell1"
    sell_order1["side"] = "SELL"
    sell_order1["price"] = 95.0
    sell_order1["timestamp"] = (sample_timestamp + timedelta(seconds=1)).isoformat()

    client.post("/place", json={"orders": [sell_order1]})

    # Match at T+1 to execute first trade
    match1_response = client.post("/match", json={"timestamp": sell_order1["timestamp"]})
    assert match1_response.status_code == 200

    # Place buy at 105 at T+2 seconds
    buy_order2 = sample_limit_order.copy()
    buy_order2["order_id"] = "buy2"
    buy_order2["price"] = 105.0
    buy_order2["timestamp"] = (sample_timestamp + timedelta(seconds=2)).isoformat()
    client.post("/place", json={"orders": [buy_order2]})

    # Place crossing sell at 100 at T+3 seconds
    sell_order2 = sample_limit_order.copy()
    sell_order2["order_id"] = "sell2"
    sell_order2["side"] = "SELL"
    sell_order2["price"] = 100.0
    sell_order2["timestamp"] = (sample_timestamp + timedelta(seconds=3)).isoformat()
    client.post("/place", json={"orders": [sell_order2]})

    # Match at T+3 to execute second trade
    match2_response = client.post("/match", json={"timestamp": sell_order2["timestamp"]})
    assert match2_response.status_code == 200

    # Verify 2 trades are accumulated
    response = client.get("/trades")
    assert response.status_code == 200
    trades = response.json()["trades"]
    assert len(trades) == 2

    # Check fields of the first trade
    trade = trades[0]
    for field in ["side", "price", "size", "incoming_order_id", "book_order_id", "execution", "trade_id", "timestamp"]:
        assert field in trade

    # Filter trades by timestamp
    filter_time = sample_timestamp + timedelta(seconds=2)
    filtered_response = client.get(f"/trades?from_timestamp={filter_time.isoformat()}")
    assert filtered_response.status_code == 200
    filtered_trades = filtered_response.json()["trades"]
    assert len(filtered_trades) == 1
    assert filtered_trades[0]["incoming_order_id"] == "sell2"
