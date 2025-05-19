from fastapi.testclient import TestClient
from typing import Any, Dict, Callable


def test_create_pet(
    client: TestClient,
    created_test_owner: Dict[str, Any],
    test_pet_data_factory: Callable[..., Dict[str, Any]],
) -> None:
    pet_data = test_pet_data_factory(owner_id=created_test_owner["id"])
    pet_data["name"] = "New Buddy"

    response = client.post("/pets/", json=pet_data)
    assert response.status_code == 200
    created_pet = response.json()
    assert created_pet["name"] == pet_data["name"]
    assert created_pet["owner_id"] == created_test_owner["id"]
    assert "id" in created_pet

    owner_response = client.get(f"/owners/{created_test_owner['id']}")
    owner_data = owner_response.json()
    assert any(p["id"] == created_pet["id"] for p in owner_data["pets"])


def test_read_pet(client: TestClient, created_test_pet: Dict[str, Any]) -> None:
    pet_id = created_test_pet["id"]
    response = client.get(f"/pets/{pet_id}")
    assert response.status_code == 200
    pet = response.json()
    assert pet["id"] == pet_id
    assert pet["name"] == created_test_pet["name"]


def test_read_pet_not_found(client: TestClient) -> None:
    response = client.get("/pets/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Pet not found"}


def test_read_pets_empty(client: TestClient) -> None:
    response = client.get("/pets/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_pets_with_data(
    client: TestClient,
    created_test_pet: Dict[str, Any],
    test_pet_data_factory: Callable[..., Dict[str, Any]],
    created_test_owner: Dict[str, Any],
) -> None:
    pet_data_2 = test_pet_data_factory(owner_id=created_test_owner["id"])
    pet_data_2["name"] = "Second Pet"
    client.post("/pets/", json=pet_data_2)

    response = client.get("/pets/")
    assert response.status_code == 200
    pets = response.json()
    assert len(pets) >= 2
    assert any(p["name"] == created_test_pet["name"] for p in pets)
    assert any(p["name"] == pet_data_2["name"] for p in pets)


def test_read_pets_pagination(
    client: TestClient,
    test_pet_data_factory: Callable[..., Dict[str, Any]],
    created_test_owner: Dict[str, Any],
) -> None:
    for i in range(5):
        pet_data = test_pet_data_factory(owner_id=created_test_owner["id"])
        pet_data["name"] = f"Paginated Pet {i}"
        client.post("/pets/", json=pet_data)

    response_limit_2 = client.get("/pets/?skip=0&limit=2")
    assert response_limit_2.status_code == 200
    data_limit_2 = response_limit_2.json()
    assert len(data_limit_2) == 2

    response_skip_2_limit_2 = client.get("/pets/?skip=2&limit=2")
    assert response_skip_2_limit_2.status_code == 200
    data_skip_2_limit_2 = response_skip_2_limit_2.json()
    assert len(data_skip_2_limit_2) == 2
    assert data_limit_2[0]["id"] != data_skip_2_limit_2[0]["id"]
