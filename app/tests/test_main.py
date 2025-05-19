from fastapi.testclient import TestClient

def test_read_main(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "app is running"}

def test_list_tables(client: TestClient):
    response = client.get("/tables")
    assert response.status_code == 200
    
    data = response.json()

    assert "tables" in data

    assert "owner" in data["tables"]
    assert "pet" in data["tables"]
    assert "appointment" in data["tables"]