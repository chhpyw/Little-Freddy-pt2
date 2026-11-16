"""Preview known built-in card corrections; --apply backs up before updating.

Custom/manual or edited cards are preserved. Scheduling and review rows never change.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.vocabulary_updates import updateBuiltinVocabulary


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--database', default=os.environ.get('FREDDY_PROGRESS_DATABASE', str(ROOT / 'progress.sqlite3')))
  parser.add_argument('--apply', action='store_true')
  args = parser.parse_args()
  print(json.dumps(updateBuiltinVocabulary(args.database, args.apply), indent=2))
