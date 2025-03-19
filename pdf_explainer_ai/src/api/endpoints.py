from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.pdf_processor import load_pdf, split_text
from src.core.vector_store import create_vector_store, query_pdf
from src.core.rag_generator import generate_response
from src.config import UPLOAD_DIR
from src.utils import save_uploaded_file
from src.db.mongo import save_chat_history, get_pdf_metadata
from src.api.save_pdf_metadata import save_pdf_metadata,save_pdf_content,get_chat_history,fs
import os 
from fastapi.responses import FileResponse
import tempfile



router = APIRouter()

# Store Chroma collections in a dict (keyed by PDF ID)
collections = {}

# Maximum file size limit (e.g., 10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file, save metadata and content to MongoDB, and process for chat."""
    # Check file extension
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Check file size before processing
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds limit of {MAX_FILE_SIZE // (1024 * 1024)} MB"
        )

    # Save the file to disk
    try:
        file_path = save_uploaded_file(file, UPLOAD_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Extract text from PDF
    pdf_texts = load_pdf(file_path)
    if not pdf_texts:
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF.")

    # Save metadata to MongoDB
    try:
        pdf_id = save_pdf_metadata(file_path, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save metadata: {str(e)}")

    # Save PDF content to GridFS
    try:
        save_pdf_content(file_path, pdf_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save PDF content: {str(e)}")

    # Process text into chunks and create a vector store
    try:
        token_split_texts = split_text(pdf_texts)
        collections[pdf_id] = create_vector_store(token_split_texts, collection_name=pdf_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF for chat: {str(e)}")

    return {
        "message": f"PDF {file.filename} uploaded and processed successfully.",
        "pdf_id": pdf_id
    }

@router.post("/chat/")
async def chat_with_pdf(pdf_id: str, query: str):
    """Chat with the uploaded PDF using its ID."""
    if pdf_id not in collections:
        raise HTTPException(status_code=404, detail="No PDF found with that ID")
    
    # Retrieve relevant chunks from the vector store
    retrieved_docs = query_pdf(collections[pdf_id], query)
    if not retrieved_docs:
        raise HTTPException(status_code=404, detail="No relevant content found in the PDF")
    
    # Generate response based on query and retrieved content
    answer = generate_response(query, retrieved_docs)
    
    # Save chat history to MongoDB
    save_chat_history(pdf_id, query, answer)
    
    return {
        "query": query,
        "answer": answer,
        "pdf_id": pdf_id
    }
    
    

@router.get("/get-pdf/{pdf_id}")
async def get_pdf(pdf_id: str, metadata_only: bool = False):
    """Fetch the uploaded PDF file or its metadata by pdf_id from GridFS."""
    pdf_metadata = get_pdf_metadata(pdf_id)
    if not pdf_metadata:
        raise HTTPException(status_code=404, detail="PDF not found")

    if metadata_only:
        return pdf_metadata
    
    pdf_file = fs.get_last_version(filename=pdf_id)
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF file not found in GridFS")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name
    
    return FileResponse(
        path=tmp_path,
        media_type="application/pdf",
        filename=pdf_metadata["filename"]
    )

@router.get("/get-chat-history/{pdf_id}")
async def get_chat_history_endpoint(pdf_id: str):
    """Retrieve chat history for a specific PDF by pdf_id."""
    try:
        chat_history = get_chat_history(pdf_id)
        if not chat_history:
            return {"pdf_id": pdf_id, "chat_history": [], "message": "No chat history found for this PDF"}
        return {"pdf_id": pdf_id, "chat_history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")