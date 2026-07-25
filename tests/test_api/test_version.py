from fastapi.testclient import TestClient

from order_matching import __version__


def test_get_version(client: TestClient) -> None:
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == __version__
