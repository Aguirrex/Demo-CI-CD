from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Callable


def test_create_appointment(
    client: TestClient,
    created_test_pet: Dict[str, Any],
    test_appointment_data_factory: Callable[..., Dict[str, Any]],
) -> None:
    appointment_dt = datetime.now(timezone.utc) + timedelta(days=5)
    appointment_data = test_appointment_data_factory(
        pet_id=created_test_pet["id"], appointment_time=appointment_dt
    )
    appointment_data["reason"] = "Follow-up"

    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200
    created_appointment = response.json()
    assert created_appointment["reason"] == appointment_data["reason"]
    assert created_appointment["pet_id"] == created_test_pet["id"]
    assert "id" in created_appointment

    assert (
        created_appointment["appointment_date"]
        == appointment_dt.replace(tzinfo=None).isoformat()
    )


def test_read_appointment(
    client: TestClient, created_test_appointment: Dict[str, Any]
) -> None:
    appointment_id = created_test_appointment["id"]
    response = client.get(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    appointment = response.json()
    assert appointment["id"] == appointment_id
    assert appointment["reason"] == created_test_appointment["reason"]


def test_read_appointment_not_found(client: TestClient) -> None:
    response = client.get("/appointments/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Appointment not found"}


def test_read_appointments_empty(client: TestClient) -> None:
    response = client.get("/appointments/")
    assert response.status_code == 200
    assert response.json() == []


def test_read_appointments_with_data(
    client: TestClient,
    created_test_appointment: Dict[str, Any],
    test_appointment_data_factory: Callable[..., Dict[str, Any]],
    created_test_pet: Dict[str, Any],
) -> None:
    appointment_data_2 = test_appointment_data_factory(
        pet_id=created_test_pet["id"],
        appointment_time=datetime.now(timezone.utc) + timedelta(days=10),
    )
    appointment_data_2["reason"] = "Vaccination"
    client.post("/appointments/", json=appointment_data_2)

    response = client.get("/appointments/")
    assert response.status_code == 200
    appointments = response.json()
    assert len(appointments) >= 2
    assert any(a["reason"] == created_test_appointment["reason"] for a in appointments)
    assert any(a["reason"] == appointment_data_2["reason"] for a in appointments)


def test_read_appointments_pagination(
    client: TestClient,
    test_appointment_data_factory: Callable[..., Dict[str, Any]],
    created_test_pet: Dict[str, Any],
) -> None:
    for i in range(5):
        appt_data = test_appointment_data_factory(
            pet_id=created_test_pet["id"],
            appointment_time=datetime.now(timezone.utc) + timedelta(days=i + 1),
        )
        appt_data["reason"] = f"Paginated Appt {i}"
        client.post("/appointments/", json=appt_data)

    response_limit_2 = client.get("/appointments/?skip=0&limit=2")
    assert response_limit_2.status_code == 200
    data_limit_2 = response_limit_2.json()
    assert len(data_limit_2) == 2

    response_skip_2_limit_2 = client.get("/appointments/?skip=2&limit=2")
    assert response_skip_2_limit_2.status_code == 200
    data_skip_2_limit_2 = response_skip_2_limit_2.json()
    assert len(data_skip_2_limit_2) == 2
    assert data_limit_2[0]["id"] != data_skip_2_limit_2[0]["id"]


def test_create_appointment_invalid_date_format(
    client: TestClient, created_test_pet: Dict[str, Any]
) -> None:
    appointment_data = {
        "pet_id": created_test_pet["id"],
        "appointment_date": "not-a-valid-date",
        "reason": "Checkup with invalid date",
    }
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 422
