from pymongo import MongoClient
from src.config import MONGO_URI, MONGO_DB_NAME
import uuid
import time
from gridfs import GridFS

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
pdfs_collection = db["pdfs"]
fs = GridFS(db, collection="pdf_files", chunk_collection="file_chunks")
chat_history_collection = db["chat_history"]

def save_pdf_metadata(file_path:str, filename:str) -> str:
    pdf_doc = {
        "pdf_id" : str(uuid.uuid4()),
        "filename": filename,
        "file_path":file_path,
        "upload_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    result = pdfs_collection.insert_one(pdf_doc)
    print(pdf_doc["pdf_id"])
    return pdf_doc["pdf_id"] 




def save_pdf_content(file_path: str, pdf_id: str) -> None:
    """Save the PDF binary content to GridFS using the pdf_id."""
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    fs.put(pdf_data, filename=pdf_id, metadata={"pdf_id": pdf_id})
    
    
    

def save_chat_history(pdf_id: str, query: str, answer: str) -> None:
    """Save chat history to MongoDB."""
    chat_doc = {
        "pdf_id": pdf_id,
        "query": query,
        "answer": answer,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    chat_history_collection.insert_one(chat_doc)

def get_chat_history(pdf_id: str) -> list:
    """Retrieve chat history for a specific pdf_id from MongoDB."""
    history = chat_history_collection.find({"pdf_id": pdf_id})
    # Convert MongoDB documents to a list, removing internal '_id' field
    chat_list = [doc for doc in history]
    for doc in chat_list:
        doc.pop("_id", None)
    return chat_list