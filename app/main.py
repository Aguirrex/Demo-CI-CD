from fastapi import FastAPI
from app.routes import pets, owners, appointments
from app.db.database import engine, Base
from sqlalchemy import inspect, text, Inspector
from typing import Dict, List, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.exc import OperationalError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        Base.metadata.drop_all(bind=engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)
        print("Database connected and tables created.")
    except OperationalError as e:
        print(f"Database is not available: {e}")

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_main() -> Dict[str, str]:
    return {"msg": "app is running"}


@app.get("/tables")
def list_tables() -> Dict[str, List[str]]:
    inspector: Inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}


app.include_router(pets.router, prefix="/pets", tags=["Pets"])
app.include_router(owners.router, prefix="/owners", tags=["Owners"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
