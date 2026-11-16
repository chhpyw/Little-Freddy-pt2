"""Exercise real Flask HTTP and Ollama with synthetic dialogue and isolated data."""
import json
import logging
import os
from pathlib import Path
import sys
import tempfile
import threading
import time

import requests
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
  rows, events = [], []
  class Capture(logging.Handler):
    def emit(self, record):
      message = record.getMessage()
      if message.startswith('tutor_event '):
        events.append(json.loads(message[len('tutor_event '):]))
  with tempfile.TemporaryDirectory(prefix='freddy-restaurant-') as directory:
    os.environ.update(FREDDY_UPLOAD_FOLDER=directory + '/uploads',
                      FREDDY_INDEX_FILE=directory + '/index.json',
                      FREDDY_PROGRESS_DATABASE=directory + '/progress.sqlite3')
    import app as backend
    backend.app.logger.addHandler(Capture())
    server = make_server('127.0.0.1', 0, backend.app, threaded=True)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    session = requests.Session()
    session.trust_env = False
    history = []
    turns = [
      "Let's practice ordering food at a Thai restaurant. I am a beginner.",
      'I would like one plate of non-spicy fried rice, please.',
      'Can I add one glass of water?',
      'Can you show the pronunciation again?',
      'How do I ask the price?',
      'How do I say thank you at the end?'
    ]
    expected = ['food-rice', 'food-rice', 'food-water', 'food-water', 'shopping-price', 'food-thanks']
    try:
      for query, target in zip(turns, expected):
        events.clear()
        pending = history + [dict(role='user', content=query)]
        started = time.monotonic()
        response = session.post(f'http://127.0.0.1:{server.server_port}/chat',
          json=dict(messages=pending, tutor=dict(level='Beginner', mode='Roleplay', pronunciation=True)), timeout=140)
        body = response.json()
        ids = [item.get('id') for item in body.get('reviewed_examples', [])]
        usable = response.status_code == 200 and body.get('script_validation') == 'thai-fields-v1' and target in ids
        rows.append(dict(learner=query, status=response.status_code, seconds=round(time.monotonic()-started, 2),
                         usable=usable, response=body, diagnostics=list(events)))
        print(json.dumps(dict(learner=query, status=response.status_code, usable=usable,
                              kind=body.get('response_kind'), model=body.get('model'))), flush=True)
        history = pending
        if usable and body.get('ai_commentary_accepted') is True:
          history.append(dict(role='assistant', content=body['response'], teaching=body['teaching'],
                              reviewed_examples=body['reviewed_examples'], script_validation=body['script_validation']))
    finally:
      server.shutdown()
      worker.join()
      server.server_close()
    report = dict(transport='real HTTP Werkzeug Flask -> real Ollama; no generation mocks',
                  configured_model=backend.CHAT_MODEL, turns=rows,
                  usable=sum(row['usable'] for row in rows),
                  ai_accepted=sum(row['response'].get('ai_commentary_accepted') is True for row in rows),
                  fallbacks=sum(row['response'].get('response_kind') == 'reviewed_fallback' for row in rows))
    (ROOT / 'docs/restaurant-flow-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if all(row['usable'] for row in rows) else 1


if __name__ == '__main__':
  raise SystemExit(main())
