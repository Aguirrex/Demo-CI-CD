import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone # Added timezone for robust datetime handling

from app.main import app
from app.db.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):

    original_override = app.dependency_overrides.get(get_db)


    def _override_get_db_for_client():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db_for_client
    
    with TestClient(app) as c:
        yield c
    
    if original_override:
        app.dependency_overrides[get_db] = original_override
    else:
        app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(scope="function")
def test_owner_data_factory():
    def _factory(email_suffix=""):
        return {
            "full_name": "Test Owner",
            "email": f"test.owner{email_suffix}@example.com",
            "phone_number": "1234567890"
        }
    return _factory

@pytest.fixture(scope="function")
def created_test_owner(client, test_owner_data_factory):
    owner_data = test_owner_data_factory()
    response = client.post("/owners/", json=owner_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="function")
def test_pet_data_factory(created_test_owner):
    def _factory(owner_id=None):
        return {
            "name": "Test Pet",
            "species": "Dog",
            "breed": "Labrador",
            "age": 3,
            "owner_id": owner_id or created_test_owner["id"]
        }
    return _factory

@pytest.fixture(scope="function")
def created_test_pet(client, test_pet_data_factory):
    pet_data = test_pet_data_factory()
    response = client.post("/pets/", json=pet_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="function")
def test_appointment_data_factory(created_test_pet):
    def _factory(pet_id=None, appointment_time=None):
        appointment_dt = appointment_time or datetime.now(timezone.utc)
        return {
            "pet_id": pet_id or created_test_pet["id"],
            "appointment_date": appointment_dt.isoformat(),
            "reason": "Regular checkup"
        }
    return _factory

@pytest.fixture(scope="function")
def created_test_appointment(client, test_appointment_data_factory):
    appointment_data = test_appointment_data_factory()
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200
    return response.json()