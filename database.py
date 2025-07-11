import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password123@20.119.98.41:27018/admin")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    # Intentar una operación para verificar la conexión
    client.admin.command('ping')
    db = client["CraftyGram"]
except ConnectionFailure as e:
    print(f"Error de conexión a MongoDB: {e}")
    db = None