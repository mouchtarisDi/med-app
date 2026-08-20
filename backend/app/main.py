from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.api.auth import router as auth_router

app = FastAPI(title="Medical Practice Management API")

# Include routing module for authentication endpoints
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/health/db")
def test_db_connection(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"database_connected": bool(result)}