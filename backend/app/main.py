from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

app = FastAPI(title="Medical Practice Management API")

@app.get("/")
def read_root():
    return {"message": "API is running"}

# Test route to verify PostgreSQL connection
@app.get("/health/db")
def test_db_connection(db: Session = Depends(get_db)):
    # Executes a simple SQL query to test connectivity
    result = db.execute(text("SELECT 1")).scalar()
    return {"database_connected": bool(result)}