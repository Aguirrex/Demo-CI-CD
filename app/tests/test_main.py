from fastapi.testclient import TestClient


def test_read_main(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    response_json = response.json()
    assert "msg" in response_json
    assert isinstance(response_json["msg"], str)