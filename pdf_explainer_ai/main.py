from pdf_processor import load_pdf, split_text
from vector_store import create_vector_store,query_pdf
from rag_generator import generate_response


def process_and_query_pdf(file_path = "dummy.pdf"):
    """Main function to process a PDF and handle user queries"""
    pdf_texts = load_pdf(file_path)
    if not pdf_texts:
        print("No content found in the PDF")
        return
    
    token_split_texts = split_text(pdf_texts)
    chroma_collection = create_vector_store(token_split_texts)
    print(chroma_collection)
    print("PDF processed successfully. You can now ask questions. ")
    while True:
        query = input("Ask a question about the PDF (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        retrived_docs = query_pdf(chroma_collection,query)
        answer = generate_response(query, retrived_docs)
        print("\nAnswer:")
        print(answer)
        print("-" * 50)
        

if __name__ == "__main__":
    print("Processing the file... ")
    process_and_query_pdf("./data/data.pdf")