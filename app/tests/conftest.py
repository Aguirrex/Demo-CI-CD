import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Connection, Transaction
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone
from typing import Any, Generator, Callable, Dict, cast

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    connection: Connection = engine.connect()
    transaction: Transaction = connection.begin()

    session: Session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:

    original_override: Any = app.dependency_overrides.get(get_db)

    def _override_get_db_for_client() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db_for_client

    with TestClient(app) as c:
        yield c

    if original_override:
        app.dependency_overrides[get_db] = original_override
    else:
        app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_owner_data_factory() -> Callable[..., Dict[str, Any]]:
    def _factory(email_suffix: str = "") -> Dict[str, Any]:
        return {
            "full_name": "Test Owner",
            "email": f"test.owner{email_suffix}@example.com",
            "phone_number": "1234567890",
        }

    return _factory


@pytest.fixture(scope="function")
def created_test_owner(
    client: TestClient, test_owner_data_factory: Callable[..., Dict[str, Any]]
) -> Dict[str, Any]:
    owner_data = test_owner_data_factory()
    response = client.post("/owners/", json=owner_data)
    assert response.status_code == 200
    return cast(Dict[str, Any], response.json())


@pytest.fixture(scope="function")
def test_pet_data_factory(
    created_test_owner: Dict[str, Any],
) -> Callable[..., Dict[str, Any]]:
    def _factory(owner_id: int | None = None) -> Dict[str, Any]:
        return {
            "name": "Test Pet",
            "species": "Dog",
            "breed": "Labrador",
            "age": 3,
            "owner_id": owner_id or created_test_owner["id"],
        }

    return _factory


@pytest.fixture(scope="function")
def created_test_pet(
    client: TestClient, test_pet_data_factory: Callable[..., Dict[str, Any]]
) -> Dict[str, Any]:
    pet_data = test_pet_data_factory()
    response = client.post("/pets/", json=pet_data)
    assert response.status_code == 200
    return cast(Dict[str, Any], response.json())


@pytest.fixture(scope="function")
def test_appointment_data_factory(
    created_test_pet: Dict[str, Any],
) -> Callable[..., Dict[str, Any]]:
    def _factory(
        pet_id: int | None = None, appointment_time: datetime | None = None
    ) -> Dict[str, Any]:
        appointment_dt = appointment_time or datetime.now(timezone.utc)
        return {
            "pet_id": pet_id or created_test_pet["id"],
            "appointment_date": appointment_dt.isoformat(),
            "reason": "Regular checkup",
        }

    return _factory


@pytest.fixture(scope="function")
def created_test_appointment(
    client: TestClient, test_appointment_data_factory: Callable[..., Dict[str, Any]]
) -> Dict[str, Any]:
    appointment_data = test_appointment_data_factory()
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200
    return cast(Dict[str, Any], response.json())
