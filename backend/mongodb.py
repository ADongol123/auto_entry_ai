import os  # Add this line to import the os module
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://aayush:aayush@cluster0.gztz2.mongodb.net/")
DB_NAME = "bills"
COLLECTION_NAME = "parsed_bills"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_to_mongodb(img_path, text):
    """Save extracted text and structured data to MongoDB."""
    document = {
        "image_path": img_path,
        "raw_text": text,
        # "structured_data": structured_data,
        'date_added': datetime.now()
    }

    # Insert the document into MongoDB
    collection.insert_one(document)
    print("Data saved successfully to MongoDB.")
