from typing import Any

from fastapi.testclient import TestClient


def test_reset_without_seed_clears_state(client: TestClient, *, sample_limit_order: dict[str, Any]) -> None:
    # Place order
    client.post("/place", json={"orders": [sample_limit_order]})

    # Verify orders exist
    assert client.get("/orders").json()["bids"] != {}

    # Reset
    reset_response = client.post("/reset", json={})
    assert reset_response.status_code == 200
    assert "reset successfully" in reset_response.json()["message"]

    # Verify state is cleared
    assert client.get("/orders").json()["bids"] == {}
    assert client.get("/trades").json()["trades"] == []


def test_reset_with_seed(client: TestClient, *, sample_limit_order: dict[str, Any]) -> None:
    reset_response = client.post("/reset", json={"seed": 42})
    assert reset_response.status_code == 200
    assert "reset successfully" in reset_response.json()["message"]

    # Verify we can still place orders and run matching successfully
    response = client.post("/place", json={"orders": [sample_limit_order]})
    assert response.status_code == 200
