from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import sqlite3
from sqlite3 import Connection

app = FastAPI()

# Path to the SQLite database file
DATABASE_URL = "sqlite:///./test.db"

# Pydantic model for the User
class User(BaseModel):
    id: int
    name: str
    email: str

# Dependency to get the database connection
def get_db():
    conn = sqlite3.connect("test.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.get("/search", response_model=List[User])
def search_users(q: str, conn: Connection = Depends(get_db)):
    query = "SELECT id, name, email FROM user WHERE name LIKE ? OR email = ?"
    values = (f"%{q}%", f"%{q}%")
    
    try:
        cursor = conn.execute(query, values)
        results = cursor.fetchall()
        users = [User(id=row["id"], name=row["name"], email=row["email"]) for row in results]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with: uvicorn myapp:app --reload
