"""Explicit, conservative updates for known historical built-in card snapshots."""
import json
from pathlib import Path
import sqlite3
from contextlib import closing
from uuid import uuid4

from src.vocabulary_content import catalog

CONTENT_FIELDS = ('thai', 'roman', 'english', 'category', 'example_thai',
                  'example_roman', 'example_english', 'lesson_id')


def updateBuiltinVocabulary(databasePath, apply=False):
  databasePath = Path(databasePath).resolve()
  legacy = json.loads(Path(__file__).with_name('vocabulary_legacy.json').read_text())
  current = {(word['lesson_id'], word['thai']): word
             for lesson in catalog() for word in lesson['words']}
  uri = databasePath.as_uri() + ('?mode=rw' if apply else '?mode=ro')
  connection = sqlite3.connect(uri, uri=True)
  connection.row_factory = sqlite3.Row
  try:
    if apply:
      # Lock before selecting candidates so no writer can change them during backup.
      connection.execute('BEGIN IMMEDIATE')
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE name='vocabulary'").fetchone():
      return dict(total=0, eligible=0, updated=0, preserved=0, backup=None)
    rows = connection.execute('SELECT * FROM vocabulary').fetchall()
    changes = []
    for row in rows:
      # A matching word alone is never evidence of built-in provenance.
      if not row['lesson_id']:
        continue
      for previous in legacy:
        if all(row[field] == previous[field] for field in CONTENT_FIELDS):
          latest = current.get((row['lesson_id'], row['thai']))
          if latest and any(row[field] != latest[field] for field in CONTENT_FIELDS):
            changes.append((row['id'], latest))
          break
    backup = None
    if apply and changes:
      backup = databasePath.with_name(databasePath.stem + '-before-content-' + uuid4().hex + '.sqlite3')
      # A separate reader can back up the database while our reserved write lock is held.
      with closing(sqlite3.connect(databasePath.as_uri() + '?mode=ro', uri=True)) as source:
        with closing(sqlite3.connect(backup)) as destination:
          source.backup(destination)
      for wordId, latest in changes:
        connection.execute('UPDATE vocabulary SET ' + ', '.join(field + ' = ?' for field in CONTENT_FIELDS)
                           + ' WHERE id = ?', [latest[field] for field in CONTENT_FIELDS] + [wordId])
      connection.commit()
    return dict(total=len(rows), eligible=len(changes), updated=len(changes) if apply else 0,
                preserved=len(rows) - len(changes), backup=str(backup) if backup else None)
  finally:
    connection.close()  # Uncommitted work rolls back, including any failed update.
