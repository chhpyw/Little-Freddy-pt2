"""Opt-in live Ollama smoke test. Uses synthetic content and temporary app storage only."""
import argparse
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def samplePdf():
  from pypdf import PdfWriter
  from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
  writer = PdfWriter()
  page = writer.add_blank_page(width=600, height=300)
  font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
  page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
  stream = DecodedStreamObject()
  stream.set_data(b'BT /F1 12 Tf 20 200 Td (The Bangkok practice cafe sells coconut water for 37 baht.) Tj ET')
  page[NameObject('/Contents')] = writer._add_object(stream)
  output = io.BytesIO(); writer.write(output); output.seek(0)
  return output


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--all-tutor-settings', action='store_true', help='Exercise all 12 level/mode combinations, which may take several minutes.')
  parser.add_argument('--report', help='Optional JSON result path outside learner storage.')
  args = parser.parse_args()
  results = []
  with tempfile.TemporaryDirectory(prefix='freddy-live-') as directory:
    # Configure paths before importing app so even startup uses temporary storage.
    os.environ['FREDDY_UPLOAD_FOLDER'] = str(Path(directory, 'uploads'))
    os.environ['FREDDY_INDEX_FILE'] = str(Path(directory, 'index.json'))
    os.environ['FREDDY_PROGRESS_DATABASE'] = str(Path(directory, 'learner.sqlite3'))
    import requests
    import app as backend
    session = requests.Session(); session.trust_env = False
    def check(name, success, **detail):
      result = dict(check=name, passed=bool(success), **detail)
      results.append(result); print(json.dumps(result, ensure_ascii=False), flush=True)
    try:
      tags = session.get(backend.OLLAMA_URL + '/api/tags', timeout=5)
      tags.raise_for_status()
      models = {model['name'] for model in tags.json()['models']}
      available = all(model in models or model + ':latest' in models for model in (backend.CHAT_MODEL, backend.EMBED_MODEL))
      check('configured models installed', available, chat_model=backend.CHAT_MODEL, embed_model=backend.EMBED_MODEL)
      if not available: return 1
      embedding = backend.get_embedding('A synthetic Thai lesson about a practice cafe.')
      check('live embedding', backend.valid_embedding(embedding), dimensions=len(embedding) if embedding else 0)
      client = backend.app.test_client()
      settings = [(level, mode) for level in backend.TUTOR_LEVELS for mode in backend.TUTOR_MODES] if args.all_tutor_settings else [('Beginner', 'Free Chat')]
      for level, mode in settings:
        started = time.monotonic()
        response = client.post('/chat', json={'messages': [{'role': 'user', 'content': 'Give one short Thai greeting with a brief English gloss. Keep the answer to one sentence.'}],
          'tutor': dict(level=level, mode=mode, pronunciation=True)})
        answer = (response.json or {}).get('response', '')
        check('live tutor ' + level + ' / ' + mode, response.status_code == 200 and any('\u0e01' <= c <= '\u0e2e' for c in answer),
              status=response.status_code, response_characters=len(answer), contains_thai=any("\u0e01" <= c <= "\u0e2e" for c in answer), seconds=round(time.monotonic() - started, 2))
      response = client.post('/upload', data={'file': (samplePdf(), 'freddy-smoke.pdf')})
      check('live PDF extraction and embedding upload', response.status_code == 200, status=response.status_code)
      for question, name in [('What is the coconut water price in freddy-smoke.pdf? Include the number and filename.', 'explicit PDF retrieval'),
                             ('How many baht does coconut water cost at the Bangkok practice cafe? Include the price and source filename.', 'semantic retrieval')]:
        response = client.post('/chat', json={'messages': [{'role': 'user', 'content': question}],
          'tutor': dict(level='Beginner', mode='Free Chat', pronunciation=True)})
        answer = (response.json or {}).get('response', '')
        check('live ' + name, response.status_code == 200 and '37' in answer and 'freddy-smoke.pdf' in response.json.get('doc_sources', []),
              status=response.status_code, answer_has_price='37' in answer,
              source_metadata=response.json.get('doc_sources', []), answer_cites_filename='freddy-smoke.pdf' in answer)
      response = client.delete('/files/freddy-smoke.pdf')
      check('temporary PDF deletion and index removal', response.status_code == 200 and not backend.load_index() and not Path(directory, 'uploads', 'freddy-smoke.pdf').exists())
    except requests.RequestException as error:
      check('live service connection', False, error_type=type(error).__name__)
    finally:
      if args.report:
        Path(args.report).write_text(json.dumps(results, indent=2), encoding='utf-8')
  return 0 if results and all(result['passed'] for result in results) else 1


if __name__ == '__main__':
  raise SystemExit(main())
