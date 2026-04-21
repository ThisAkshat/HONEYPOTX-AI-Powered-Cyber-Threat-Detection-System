# Use of db.py → Handles connection with MongoDB and manages database operations (insert, fetch, update logs).

from pymongo import MongoClient
import config

client = None
db = None

def init_db():
    global client, db
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]

def get_db():
    return db