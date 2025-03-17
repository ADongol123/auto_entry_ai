import os 

# Directory for temporary uploads
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../uploads")
os.makedirs(UPLOAD_DIR,exist_ok=True)

# Model settings
RAG_MODEL = "facebook/bart-large"
MAX_INPUT_LENGTH = 1000
MAX_OUTPUT_LENGTH = 300

# MongoDB settings
MONGO_URI = "mongodb+srv://ayussh222dongol:aayush@123@cluster0.sgbpc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB_NAME = "pdf_chat_db"

