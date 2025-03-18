import os
import shutil
from fastapi import UploadFile

def save_uploaded_file(file: UploadFile, upload_dir: str) -> str:
    """Save an uploaded file to the specified directory and return its path."""
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path