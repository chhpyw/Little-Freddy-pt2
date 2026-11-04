import os
import json
from app import extract_text, chunk_text, get_embedding, load_index, save_index, UPLOAD_FOLDER, INDEX_FILE

def reindex_all():
    print("Starting re-indexing of all documents...")
    index = load_index()
    count = 0
    
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            print(f"Processing {filename}...", end=" ")
            text = extract_text(filepath)
            if not text:
                print("FAILED (No text extracted)")
                continue
                
            chunks = chunk_text(text)
            doc_embeddings = []
            for chunk in chunks:
                emb = get_embedding(chunk)
                if emb:
                    doc_embeddings.append({"text": chunk, "embedding": emb})
            
            if doc_embeddings:
                index[filename] = doc_embeddings
                print(f"SUCCESS ({len(doc_embeddings)} chunks)")
                count += 1
            else:
                print("FAILED (No embeddings generated)")
    
    save_index(index)
    print(f"\nRe-indexing complete. {count} documents successfully indexed.")

if __name__ == "__main__":
    # Mocking environment variable for reindex script if missing
    if not os.environ.get("OLLAMA_API_KEY"):
        print("Warning: OLLAMA_API_KEY not found. Embeddings may fail if API requires it.")
        
    reindex_all()
