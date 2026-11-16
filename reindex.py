"""Rebuild embeddings without publishing partial document indexes.

Run with Flask stopped; do not run multiple writer processes against the JSON index.
"""
import os
import argparse
import json
import app as backend


def reindex_all(max_attempts=2, report=None):
  if max_attempts not in (1, 2, 3):
    raise ValueError('Choose one to three embedding attempts per chunk.')
  report = report if report is not None else []
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
      report.append(dict(filename=filename, status='failed', reason='No text extracted'))
      print('FAILED (No text extracted; previous index kept)')
      continue
    chunks = []
    failure = None
    dimensions = None
    for chunk_number, text_chunk in enumerate(backend.chunk_text(text), 1):
      for attempt in range(1, max_attempts + 1):
        embedding = backend.get_embedding(text_chunk)
        if backend.valid_embedding(embedding):
          break
      if not backend.valid_embedding(embedding):
        failure = f'Chunk {chunk_number}: no valid embedding after {max_attempts} attempt(s); check Ollama logs/model availability'
        chunks = []
        break
      if dimensions is not None and len(embedding) != dimensions:
        failure = f'Chunk {chunk_number}: inconsistent embedding dimensions'
        chunks = []
        break
      dimensions = len(embedding)
      chunks.append({'text': text_chunk, 'embedding': embedding})
    if not chunks:
      report.append(dict(filename=filename, status='failed', reason=failure))
      print(f'FAILED ({failure}; previous index kept)')
      continue
    with backend.DOCUMENT_LOCK:
      index = backend.load_index()
      index[filename] = chunks
      backend.save_index(index)
    count += 1
    report.append(dict(filename=filename, status='indexed', chunks=len(chunks), dimensions=dimensions))
    print(f'SUCCESS ({len(chunks)} chunks)')
  print(f'Re-indexing complete. {count} documents successfully indexed.')
  return count


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--attempts', type=int, choices=(1, 2, 3), default=2)
  parser.add_argument('--report', help='Optional JSON diagnostic report path.')
  args = parser.parse_args()
  results = []
  reindex_all(args.attempts, results)
  if args.report:
    with open(args.report, 'w', encoding='utf-8') as output:
      json.dump(results, output, indent=2)
  raise SystemExit(1 if any(row['status'] == 'failed' for row in results) else 0)
