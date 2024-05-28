import pymongo
from pymongo import MongoClient

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'open_isp'
MONGODB_COLLECTION = 'payment_data'

class DatabaseError(Exception):
    pass

def connect_to_mongodb():
    try:
        client = MongoClient(MONGODB_HOST, MONGODB_PORT)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
        return collection
    except Exception as e:
        error_message = f"Failed to connect to MongoDB: {e}"
        print(error_message)
        raise DatabaseError(error_message)

def save_to_mongodb(data):
    collection = connect_to_mongodb()
    try:
        collection.insert_many(data)
        print("Dados escritos na base de dados com sucesso.")
    except Exception as e:
        error_message = f"Failed to save data to MongoDB: {e}"
        print(error_message)
        raise DatabaseError(error_message)
