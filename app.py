from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import os
import json
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "qwen3:1.7b"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

UPLOAD_FOLDER = 'uploads'
INDEX_FILE = 'vector_index.json'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'md'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def ollama_request(endpoint, payload):
    headers = {}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
    try:
        resp = requests.post(f"{OLLAMA_URL}{endpoint}", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Ollama API Error ({endpoint}): {e}")
        return None

def load_index():
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r') as f: return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_index(index):
    with open(INDEX_FILE, 'w') as f: json.dump(index, f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    try:
        if ext == 'txt' or ext == 'md':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: return f.read()
        elif ext == 'pdf':
            # Import inside function to avoid startup crash if not installed
            import pypdf
            reader = pypdf.PdfReader(filepath)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text
        elif ext == 'docx':
            import docx
            doc = docx.Document(filepath)
            return " ".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Extraction error for {filepath}: {e}")
    return ""

def chunk_text(text, size=500):
    if not text: return []
    return [text[i:i + size] for i in range(0, len(text), size)]

def get_embedding(text):
    if not text or not text.strip(): return None
    res = ollama_request("/api/embeddings", {"model": EMBED_MODEL, "prompt": text})
    return res.get('embedding') if res else None

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0: return 0
    return np.dot(v1, v2) / (norm1 * norm2)

def perform_web_search(query):
    res = ollama_request("/api/web_search", {"query": query})
    return res.get('results') if res else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    if not messages: return jsonify({"error": "No messages provided"}), 400
    
    user_query = messages[-1].get('content', '')
    use_web_search = data.get('use_web_search', False)
    
    index = load_index()
    doc_context = []
    doc_sources = set()
    
    # 1. Handle Document Listing Questions
    query_lower = user_query.lower()
    is_collection_query = any(phrase in query_lower for phrase in ["what documents", "what files", "list your documents", "which files are uploaded"])
    
    if is_collection_query:
        # Strictly retrieve from the actual index keys
        uploaded_files = list(index.keys())
        if uploaded_files:
            file_info_list = []
            for f in uploaded_files:
                path = os.path.join(app.config['UPLOAD_FOLDER'], f)
                size = os.path.getsize(path) if os.path.exists(path) else 0
                file_info_list.append(f"{f} ({size/1024:.1f}KB)")
            
            doc_context.append(f"The current document collection consists of: {', '.join(file_info_list)}.")
            doc_sources.update(uploaded_files)
        else:
            doc_context.append("The document collection is currently empty.")
    else:
        # 2. Handle Specific Document Mention or General RAG
        explicit_doc = None
        for filename in index.keys():
            if filename.lower() in user_query.lower():
                explicit_doc = filename
                break
        
        if explicit_doc:
            chunks = index.get(explicit_doc, [])
            if chunks:
                # Use top chunks for context
                for chunk in chunks[:10]:
                    doc_context.append(chunk['text'])
                doc_sources.add(explicit_doc)
            else:
                doc_context.append(f"Document {explicit_doc} was found but contains no indexable text.")
        else:
            query_emb = get_embedding(user_query)
            if query_emb:
                all_chunks = []
                for filename, chunks in index.items():
                    for chunk in chunks:
                        sim = cosine_similarity(query_emb, chunk['embedding'])
                        all_chunks.append((sim, chunk['text'], filename))
                all_chunks.sort(key=lambda x: x[0], reverse=True)
                for sim, text, filename in all_chunks[:3]:
                    if sim > 0.3:
                        doc_context.append(text)
                        doc_sources.add(filename)

    # Web Search Integration
    web_context = []
    web_sources = []
    if use_web_search:
        search_results = perform_web_search(user_query)
        if search_results:
            for r in search_results:
                web_context.append(f"Source: {r.get('url')}\nContent: {r.get('snippet')}")
                web_sources.append(r.get('url'))
        else:
            web_context.append("Web search returned no results.")

    full_context = "\n\n".join(doc_context + web_context)
    system_prompt = (
        f"You are a helpful assistant. Use the provided context (Local Docs and Web Search) "
        f"to answer the question. If the user asks about their collection, list the files provided. "
        f"If a specific document was requested, prioritize its content. "
        f"Always cite your sources using filenames or URLs if they are provided.\n\nContext:\n{full_context}"
    )
    
    augmented_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        result = ollama_request("/api/chat", {"model": CHAT_MODEL, "messages": augmented_messages, "stream": False})
        if not result: return jsonify({"error": "Ollama failed to generate a response."}), 500
        answer = result.get('message', {}).get('content', 'No response.')
        return jsonify({"response": answer, "doc_sources": list(doc_sources), "web_sources": web_sources})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        text = extract_text(filepath)
        if not text:
            return jsonify({"error": "Could not extract text from file. Indexing failed."}), 400
            
        chunks = chunk_text(text)
        if not chunks:
            return jsonify({"error": "Document is empty. Indexing failed."}), 400

        index = load_index()
        doc_embeddings = []
        for chunk in chunks:
            emb = get_embedding(chunk)
            if emb: doc_embeddings.append({"text": chunk, "embedding": emb})
        
        if not doc_embeddings:
            return jsonify({"error": "Could not generate embeddings for document."}), 500
            
        index[filename] = doc_embeddings
        save_index(index)
        return jsonify({"message": f"File {filename} indexed successfully!"}), 200
    return jsonify({"error": "Invalid file type."}), 400

@app.route('/files', methods=['GET'])
def list_files():
    files_info = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            size_str = f"{size / 1024:.2f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.2f} MB"
            files_info.append({"name": filename, "size": size_str})
    return jsonify(files_info)

@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    filename = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
        index = load_index()
        if filename in index:
            del index[filename]
            save_index(index)
        return jsonify({"message": f"File {filename} and its index deleted!"}), 200
    return jsonify({"error": "File not found"}), 404

@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
