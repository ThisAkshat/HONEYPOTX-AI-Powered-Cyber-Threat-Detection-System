# Use of app.py → Main entry point of the project. Starts the server, initializes database, and connects all modules.
from fastapi import FastAPI
from honeypot.server import router as honeypot_router
from database.db import init_db

app = FastAPI(title="HoneypotX")

init_db()
app.include_router(honeypot_router)

@app.get("/")
def home():
    return {"message": "HoneypotX Running"}