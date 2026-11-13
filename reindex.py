"""Rebuild embeddings without publishing partial document indexes.

Run with Flask stopped; do not run multiple writer processes against the JSON index.
"""
import os
import app as backend


def reindex_all():
    print('Starting re-indexing of all documents...')
    count = 0
    # Refuse to overwrite a corrupt index. Back it up and repair it explicitly first.
    backend.load_index()
    for filename in sorted(os.listdir(backend.app.config['UPLOAD_FOLDER'])):
        filepath = backend.library_path(filename)
        if not filepath:
            continue
        print(f'Processing {filename}...', end=' ')
        text = backend.extract_text(filepath)
        if not text or not text.strip():
            print('FAILED (No text extracted; previous index kept)')
            continue
        chunks = []
        for text_chunk in backend.chunk_text(text):
            embedding = backend.get_embedding(text_chunk)
            if not embedding:
                chunks = []
                break
            chunks.append({'text': text_chunk, 'embedding': embedding})
        if not chunks:
            print('FAILED (Incomplete embeddings; previous index kept)')
            continue
        with backend.DOCUMENT_LOCK:
            index = backend.load_index()
            index[filename] = chunks
            backend.save_index(index)
        count += 1
        print(f'SUCCESS ({len(chunks)} chunks)')
    print(f'Re-indexing complete. {count} documents successfully indexed.')
    return count


if __name__ == '__main__':
    reindex_all()
