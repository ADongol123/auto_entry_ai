import os 
from urllib.parse import quote_plus

# Directory for temporary uploads
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../uploads")
os.makedirs(UPLOAD_DIR,exist_ok=True)

# Model settings
RAG_MODEL = "facebook/bart-large"
MAX_INPUT_LENGTH = 1000
MAX_OUTPUT_LENGTH = 300

# MongoDB settings
username= "ayussh222dongol"
password = "aayush@123"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.sgbpc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB_NAME = "pdf_chat_db"

