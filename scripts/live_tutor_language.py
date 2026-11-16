"""Live script-safety evaluation with synthetic conversations and isolated storage.

Records actual rejected candidates for diagnosis; never use personal conversations.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.config import DEFAULT_CHAT_MODEL


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--model', default=os.environ.get('CHAT_MODEL', DEFAULT_CHAT_MODEL))
  parser.add_argument('--repeats', type=int, choices=range(1, 6), default=3)
  parser.add_argument('--report', required=True)
  args = parser.parse_args()
  results = []
  with tempfile.TemporaryDirectory(prefix='freddy-language-') as directory:
    os.environ.update(CHAT_MODEL=args.model, FREDDY_UPLOAD_FOLDER=directory + '/uploads',
                      FREDDY_INDEX_FILE=directory + '/index.json', FREDDY_PROGRESS_DATABASE=directory + '/learner.sqlite3')
    import app as backend
    from src.tutor_response import parseTeaching
    from src.tutor_curriculum import REVIEWED_EXAMPLES, parseReviewed
    original = backend.ollama_request
    attempts = []
    def tracked(endpoint, payload):
      result = original(endpoint, payload)
      if endpoint == '/api/chat':
        content = (result or {}).get('message', {}).get('content')
        try:
          properties = payload.get('format', {}).get('properties', {})
          if 'example_ids' in properties:
            ids = properties['example_ids']['items']['enum']
            parseReviewed(content, [REVIEWED_EXAMPLES[key] for key in ids], pronunciation=True)
          else:
            parseTeaching(content, pronunciation=True)
          error = None
        except (ValueError, TypeError) as failure:
          error = str(failure)
        attempts.append(dict(content=content, rejection=error))
      return result
    backend.ollama_request = tracked
    cases = {
      'greeting': [dict(role='user', content='Give one short Thai greeting with English meaning and a pronunciation guide.')],
      'food-ordering': [dict(role='user', content='Teach me to order one plate of non-spicy fried rice in Thai, with English meaning and pronunciation.')],
      'correct-wrong-language': [dict(role='user', content='Teach me to order water in Thai.'),
        dict(role='assistant', content='Thai example: မင်္ဂလာပါ ထမင်း'),
        dict(role='user', content='That is Burmese, not Thai. Correct the language error. Teach me to order one glass of water in actual Thai, with English meaning and pronunciation.')],
      'language-discussion': [dict(role='user', content='Discuss the Burmese greeting မင်္ဂလာပါ as an explicitly labeled Burmese quotation, and separately teach the Thai greeting with English meaning and pronunciation.')]
    }
    for repeat in range(args.repeats):
      for name, messages in cases.items():
        attempts.clear()
        start = time.monotonic()
        response = backend.app.test_client().post('/chat', json=dict(messages=messages,
          tutor=dict(level='Intermediate', mode='Free Chat', pronunciation=True)))
        body = response.json or {}
        result = dict(model=args.model, case=name, repeat=repeat + 1, status=response.status_code,
                      passed=response.status_code == 200 and body.get('ai_commentary_accepted') is True,
                      usable=response.status_code == 200 and body.get('script_validation') == 'thai-fields-v1',
                      fallback=body.get('response_kind') == 'reviewed_fallback', seconds=round(time.monotonic() - start, 2),
                      response=body, attempts=list(attempts))
        results.append(result)
        print(json.dumps({key:result[key] for key in ('model', 'case', 'repeat', 'status', 'passed', 'seconds')}) , flush=True)
    Path(args.report).write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
  return 0 if all(row['passed'] for row in results) else 1


if __name__ == '__main__':
  raise SystemExit(main())
