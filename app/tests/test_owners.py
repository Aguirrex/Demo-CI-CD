from fastapi.testclient import TestClient


def test_create_owner(client: TestClient, test_owner_data_factory):
    owner_data = test_owner_data_factory(email_suffix="_create_owner")
    response = client.post("/owners/", json=owner_data)
    assert response.status_code == 200
    created_owner = response.json()
    assert created_owner["email"] == owner_data["email"]
    assert "id" in created_owner
    assert created_owner["full_name"] == owner_data["full_name"]
    assert created_owner["pets"] == []


def test_read_owner(client: TestClient, created_test_owner):
    owner_id = created_test_owner["id"]
    response = client.get(f"/owners/{owner_id}")
    assert response.status_code == 200
    owner = response.json()
    assert owner["id"] == owner_id
    assert owner["email"] == created_test_owner["email"]


def test_read_owner_not_found(client: TestClient):
    response = client.get("/owners/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Owner not found"}


def test_read_owners_empty(client: TestClient):
    response = client.get("/owners/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_owners_with_data(
    client: TestClient, created_test_owner, test_owner_data_factory
):
    owner_data_2 = test_owner_data_factory(email_suffix="_owner2")
    client.post("/owners/", json=owner_data_2)

    response = client.get("/owners/")
    assert response.status_code == 200
    owners = response.json()
    assert len(owners) >= 2
    assert any(o["email"] == created_test_owner["email"] for o in owners)
    assert any(o["email"] == owner_data_2["email"] for o in owners)


def test_read_owners_pagination(client: TestClient, test_owner_data_factory):
    for i in range(5):
        client.post(
            "/owners/", json=test_owner_data_factory(email_suffix=f"_page_owner{i}")
        )

    response_limit_2 = client.get("/owners/?skip=0&limit=2")
    assert response_limit_2.status_code == 200
    data_limit_2 = response_limit_2.json()
    assert len(data_limit_2) == 2

    response_skip_2_limit_2 = client.get("/owners/?skip=2&limit=2")
    assert response_skip_2_limit_2.status_code == 200
    data_skip_2_limit_2 = response_skip_2_limit_2.json()
    assert len(data_skip_2_limit_2) == 2

    assert data_limit_2[0]["id"] != data_skip_2_limit_2[0]["id"]
