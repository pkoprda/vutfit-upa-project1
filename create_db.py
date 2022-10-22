from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = 'demo'
MONGO_PASS = 'demo'
MONGO_DB = 'messages'
MONGO_COLL = 'message_items'

def get_db(db_name: str = MONGO_DB, host: str = MONGO_HOST, port: int = MONGO_PORT) -> Database:
  database: Database = MongoClient(host, port)[db_name]
  return database

def get_collection(db: Database, coll_name: str = MONGO_COLL) -> Collection:
  return db[coll_name]
