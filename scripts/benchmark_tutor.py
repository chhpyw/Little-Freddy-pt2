"""Human-reviewable semantic benchmark; deterministic checks are not fluency grades."""
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
  parser.add_argument('--report', required=True)
  args = parser.parse_args()
  cases = json.loads((ROOT / 'tests/tutor_semantic_benchmark.json').read_text())
  results = []
  with tempfile.TemporaryDirectory(prefix='freddy-semantic-') as directory:
    os.environ.update(CHAT_MODEL=args.model, FREDDY_UPLOAD_FOLDER=directory + '/uploads',
                      FREDDY_INDEX_FILE=directory + '/index.json', FREDDY_PROGRESS_DATABASE=directory + '/learner.sqlite3')
    import app as backend
    for case in cases:
      started = time.monotonic()
      response = backend.app.test_client().post('/chat', json=dict(messages=[dict(role='user', content=case['prompt'])],
        tutor=dict(level='Beginner', mode='Guided Lesson', pronunciation=True)))
      body = response.json or {}
      examples = body.get('teaching', {}).get('examples', [])
      fixedMatch = any(example == case['expected'] for example in examples)
      sources = body.get('reviewed_examples', [])
      sourceMatch = any(item['id'] == case['expected_example_id'] for item in sources)
      result = dict(model=args.model, case=case, status=response.status_code,
                    seconds=round(time.monotonic() - started, 2),
                    schema_accepted=response.status_code == 200 and body.get('ai_commentary_accepted') is True,
                    fallback=body.get('response_kind') == 'reviewed_fallback',
                    fixed_meaning_matches_golden=fixedMatch and sourceMatch,
                    generated_semantic_review='pending_editorial_review', response=body)
      results.append(result)
      print(json.dumps(dict(model=args.model, case=case['id'], status=response.status_code,
                            fixed_meaning_matches_golden=result['fixed_meaning_matches_golden'])), flush=True)
    Path(args.report).write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
  return 0 if all(row['schema_accepted'] and row['fixed_meaning_matches_golden'] for row in results) else 1


if __name__ == '__main__':
  raise SystemExit(main())
