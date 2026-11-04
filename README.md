# Ollama Hybrid RAG Chatbot

A local web application that combines Large Language Models (LLM) with Retrieval-Augmented Generation (RAG) and Web Search.

## Features
- **Hybrid RAG**: Answer questions based on locally uploaded documents (.pdf, .txt, .docx, .md) using vector embeddings.
- **Web Search**: Toggleable real-time internet search for current events.
- **Document Management**: Simple UI to upload, view, and delete your local knowledge base.
- **Source Attribution**: Every response clearly cites the documents or URLs used to generate the answer.

## Prerequisites
- **Ollama**: Installed and running on `localhost:11434`.
- **Python 3.9+**: Installed on your local machine.

### Required Ollama Models
Pull the following models before running the application:
```bash
ollama pull qwen3:1.7b
ollama pull nomic-embed-text
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd codex-ollama
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   Set your Ollama API key as an environment variable to enable Web Search and authenticated requests:
   ```bash
   # macOS/Linux
   export OLLAMA_API_KEY='your_api_key_here'

   # Windows (PowerShell)
   $env:OLLAMA_API_KEY='your_api_key_here'
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   python3 app.py
   ```
2. Open your browser and navigate to:
   `http://127.0.0.1:5000`

## Project Structure
- `app.py`: Flask backend logic, RAG pipeline, and Ollama API integration.
- `templates/index.html`: Frontend chat and document management interface.
- `static/style.css`: Application styling.
- `requirements.txt`: Python dependencies.
- `uploads/`: (Ignored) Local storage for uploaded documents.
- `vector_index.json`: (Ignored) Local vector store for document embeddings.
