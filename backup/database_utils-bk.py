# database_utils.py

from pymongo import MongoClient

# MongoDB connection details
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB = 'open_isp'
MONGODB_COLLECTION = 'payment_data'

def connect_to_mongodb():
    try:
        client = MongoClient(MONGODB_HOST, MONGODB_PORT)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def save_to_mongodb(data):
    collection = connect_to_mongodb()
    try:
        collection.insert_many(data)
        print("Data saved to MongoDB successfully.")
        print("Dados escritos na base de dados com sucesso.")
    except Exception as e:
        print(f"Failed to save data to MongoDB: {e}")
        raise
