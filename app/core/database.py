import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings


def connect_to_mongo(retries=5, delay=2):
    for attempt in range(retries):
        try:
            client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            return client
        except ConnectionFailure:
            if attempt < retries - 1:
                print(
                    f"MongoDB not ready, retrying in {delay}s... (attempt {attempt + 1}/{retries})"
                )
                time.sleep(delay)
            else:
                raise


client = connect_to_mongo()
db = client[settings.DATABASE_NAME]

users_collection = db["users"]
products_collection = db["products"]
orders_collection = db["orders"]


def get_db():
    return db
