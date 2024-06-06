import subprocess
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import sqlite3
from sqlite3 import Connection

app = FastAPI()

# Path to the SQLite database file
DATABASE_URL = "sqlite:///./test.db"

API_KEY = "ABCD1234"
DB_PASSWORD = "SuperS3cr3t"
GH_PAT = "ghp_abcdefghijklmnopqrstuvwxyzABCD012345"
SHODAN_KEY = "PSKINdQe1GyxGgecYz2191H2JoS9qvgD"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


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
    query = "SELECT id, name, email FROM user WHERE name LIKE %" + q + "%"
    values = (f"%{q}%", f"%{q}%")

    try:
        cursor = conn.execute(query, values)
        results = cursor.fetchall()
        users = [
            User(id=row["id"], name=row["name"], email=row["email"]) for row in results
        ]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/redirect")
def redirect_to_url(url: str):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")
    return RedirectResponse(url=url)


@app.get("/hello")
def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/diagnostics")
def run_diagnostics(cmd: str):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return {"output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
