from pymongo import MongoClient
from src.config import MONGO_URI, MONGO_DB_NAME
import datetime
from bson import ObjectId

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def save_pdf(file_path:str, filename:str, pdf_texts: list) -> str:
    """Save PDF faile and extracted text to MongoDB, return document ID."""
    with open(file_path, 'rb') as f:
        pdf_binary = f.read()
        
    pdf_doc = {
        "filename":filename,
        "pdf_binary": pdf_binary,
        "extracted_text": "\n\n".join(pdf_texts)
    }
    result = db.pdfs.insert_one(pdf_doc)
    return  str(result.inserted_id)




def save_chat_history(pdf_id:str, query:str, answer:str):
    """Save chat query and answer linked to a PDF"""
    chat_doc = {
        "pdf_id": pdf_id,
        "query": query,
        "answer": answer,
        "timestamp": datetime.datetime.utcnow()
    }
    db.chat_history.insert_one(chat_doc)
    


def get_pdf_by_id(pdf_id:str):
    """Retrieve PDF document by ID"""
    return db.pdfs.find_one({
        "id": ObjectId(pdf_id)
    })