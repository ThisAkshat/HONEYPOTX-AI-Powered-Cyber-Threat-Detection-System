# Use of logger.py → Records all attacker activities (requests, commands, attempts) and stores them in the database.

from database.db import get_db
from database.model import log_schema

def log_attack(data):
    db = get_db()
    db.logs.insert_one(log_schema(data))