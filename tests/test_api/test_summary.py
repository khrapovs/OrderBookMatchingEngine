from typing import Any

from fastapi.testclient import TestClient


def test_summary_empty_book(client: TestClient) -> None:
    response = client.get("/summary")
    assert response.status_code == 200
    assert response.json() == []


def test_summary_with_orders(client: TestClient, sample_limit_order: dict[str, Any]) -> None:
    # Place buy at 100 size 10
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place buy at 100 size 5 with different ID
    order2 = sample_limit_order.copy()
    order2["order_id"] = "order2"
    order2["size"] = 5.0
    client.post("/place", json={"orders": [order2]})

    # Place buy at 105 size 7
    order3 = sample_limit_order.copy()
    order3["order_id"] = "order3"
    order3["price"] = 105.0
    order3["size"] = 7.0
    client.post("/place", json={"orders": [order3]})

    # Place sell at 200 size 30
    order4 = sample_limit_order.copy()
    order4["order_id"] = "order4"
    order4["side"] = "SELL"
    order4["price"] = 200.0
    order4["size"] = 30.0
    client.post("/place", json={"orders": [order4]})

    response = client.get("/summary")
    assert response.status_code == 200
    summary = response.json()
    assert len(summary) == 3

    # Check fields in response items
    for item in summary:
        for field in ["side", "price", "size", "count"]:
            assert field in item

    # Verify aggregation
    level_100 = next(item for item in summary if item["price"] == 100.0 and item["side"] == "BUY")
    assert level_100["size"] == 15.0
    assert level_100["count"] == 2

    level_105 = next(item for item in summary if item["price"] == 105.0)
    assert level_105["size"] == 7.0
    assert level_105["count"] == 1

    level_200 = next(item for item in summary if item["price"] == 200.0 and item["side"] == "SELL")
    assert level_200["size"] == 30.0
    assert level_200["count"] == 1
