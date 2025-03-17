from transformers import pipeline
import torch

def generate_response(query, retrieved_documents):
    """Generate a detailed response using RAG with a Hugging Face model."""
    generator = pipeline("text2text-generation", model="facebook/bart-large", device=0 if torch.cuda.is_available() else -1)
    
    context = "\n\n".join(retrieved_documents)
    if not context:
        return "I couldn't find any relevant information in the PDF to answer your question."
    
    # Improved prompt for accurate and detailed answers
    prompt = f"""
    You are a helpful assistant. The user asked: "{query}"

    Context: {context}
    Answer:
    """
    
    max_input_length = 1000
    truncated_prompt = prompt[:max_input_length]
    response = generator(
        truncated_prompt,
        max_length=500,  # Allows for longer responses
        num_return_sequences=1,
        do_sample=False  # Deterministic output for consistency
    )
    
    generated_text = response[0]["generated_text"].strip()
    if "Answer:" in generated_text:
        return generated_text.split("Answer:")[-1].strip()
    return generated_text