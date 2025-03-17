from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.pdf_processor import load_pdf, split_text
from src.core.vector_store import create_vector_store, query_pdf
from src.core.rag_generator import generate_response
from src.config import UPLOAD_DIR
from src.utils import save_uploaded_file
from src.db.mongo import save_pdf, save_chat_history



router = APIRouter()


# Store Chroma collections in a dict (keyed by PDF ID)
collections = {}

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF fille, save to MongoDB, and process for chat"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = save_uploaded_file(file, UPLOAD_DIR)
    pdf_texts = load_pdf(file_path)
    if not pdf_texts:
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF.")
    
    # Save to MongoDB
    pdf_id = save_pdf(file_path,file.filename, pdf_texts)
    
    # Process for RAG
    token_split_texts = split_text(pdf_texts)
    collections[pdf_id] = create_vector_store(token_split_texts,collection_name=pdf_id)
    
    return {
        "message": f"PDF {file.filename} uploaded and process successfully.","pdf_id":pdf_id
        }
    


@router.post("/chat/")
async def chat_with_pdf(pdf_id:str, query:str):
    """Chat with the uploaded PDF using its ID"""
    if pdf_id not in collections:
        raise HTTPException(status_code=400, detail="NO PDF found with that ID")
    
    retrived_docs = query_pdf(collections[pdf_id],query)
    answer = generate_response(query,retrived_docs)
    
    
    # Save chat history to MOngoDB
    save_chat_history(pdf_id,query,answer)
    
    return {
        "query":query,
        "answer":answer,
        "pdf_id": pdf_id
    }