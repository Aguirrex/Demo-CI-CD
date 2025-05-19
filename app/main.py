from fastapi import FastAPI
from app.routes import pets, owners, appointments
from app.db.database import engine, Base
import app.models
from sqlalchemy import inspect
from typing import Dict

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_main() -> Dict[str, str]:
    return {"msg": "app is running"}


@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    return {"tables": inspector.get_table_names()}


app.include_router(pets.router, prefix="/pets", tags=["Pets"])
app.include_router(owners.router, prefix="/owners", tags=["Owners"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
