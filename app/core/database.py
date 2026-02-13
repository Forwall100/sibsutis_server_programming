from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.DATABASE_NAME]

users_collection = db["users"]
products_collection = db["products"]
orders_collection = db["orders"]


def get_db():
    return db
