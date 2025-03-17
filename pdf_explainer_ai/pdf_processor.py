from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

def load_pdf(file_path='dummy.pdf'):
    """Load text from a PDF file"""
    try:
        reader = PdfReader(file_path)
        pdf_texts = [p.extract_text().strip() for p in reader.pages if p.extract_text()]
        return pdf_texts
    except FileNotFoundError as e:
        print(f'Error: {file_path} not found.')
        return []
    


def split_text(pdf_texts):
    """Split PDF text into chunks for embedding"""
    full_text = "\n\n".join(pdf_texts)
    character_splintter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size = 1000,
        chunk_overlap = 0
        
    )
    character_split_text = character_splintter.split_text(full_text)
    token_splinter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=0,
        tokens_per_chunk=256
    )
    
    token_split_texts = []
    for text in character_split_text:
        token_split_texts += token_splinter.split_text(text)
    return token_split_texts
