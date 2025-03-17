import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


def create_vector_store(token_split_texts, collection_name='pdf_collection'):
    """Create and populate a ChromaDB collection with text embeddings. """
    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = chromadb.Client()
    try:
        chroma_client.delete_collection(collection_name)
    except:
        pass
    chroma_collection = chroma_client.create_collection(
        collection_name,
        embedding_function=embedding_function
    )
    ids = [str(i) for i in range(len(token_split_texts))]
    chroma_collection.add(ids=ids, documents=token_split_texts)
    return chroma_collection



def query_pdf(chroma_collection, query_text, n_results = 3):
    """Query the ChromaDB collection for relevant documents."""
    results = chroma_collection.query(query_texts = [query_text], n_results=n_results)
    retrived_documents = results["documents"][0]
    return retrived_documents


