"""Safe content upgrades retain manual edits, review rows and scheduling."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

import app as backend
from src.learning import database
from src.vocabulary import saveWord
from src.vocabulary_content import catalog
from src.vocabulary_updates import updateBuiltinVocabulary, CONTENT_FIELDS


class VocabularyUpdateTests(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.path = Path(self.directory.name, 'progress.sqlite3')
    self.previous = backend.app.config['PROGRESS_DATABASE']
    backend.app.config['PROGRESS_DATABASE'] = str(self.path)
    self.context = backend.app.app_context()
    self.context.push()
    self.legacy = json.loads(Path('src/vocabulary_legacy.json').read_text())

  def tearDown(self):
    self.context.pop()
    backend.app.config['PROGRESS_DATABASE'] = self.previous
    self.directory.cleanup()

  def test_preview_backup_preserves_custom_content_and_all_review_fields(self):
    coffee = next(word for word in self.legacy if word['thai'] == 'กาแฟ')
    manual = dict(next(word for word in self.legacy if word['thai'] == 'ฉัน'), lesson_id=None)
    edited = dict(next(word for word in self.legacy if word['thai'] == 'สวัสดี'), english='My personal greeting note')
    with database() as connection:
      card = saveWord(connection, coffee)[0]
      saveWord(connection, manual)
      saveWord(connection, edited)
    client = backend.app.test_client()
    self.assertEqual(client.post(f"/api/vocabulary/{card['id']}/review", json=dict(
      quality=4, revision=0, attempt_id=str(uuid4()))).status_code, 200)
    with database() as connection:
      before = {row['id']: dict(row) for row in connection.execute('SELECT * FROM vocabulary')}
      history = [tuple(row) for row in connection.execute('SELECT * FROM vocabulary_reviews')]
    original = self.path.read_bytes()
    preview = updateBuiltinVocabulary(self.path)
    self.assertEqual((preview['total'], preview['eligible'], preview['updated']), (3, 1, 0))
    self.assertEqual(self.path.read_bytes(), original)
    result = updateBuiltinVocabulary(self.path, apply=True)
    self.assertEqual(result['updated'], 1)
    with sqlite3.connect(result['backup']) as backup:
      backup.row_factory = sqlite3.Row
      self.assertEqual({row['id']: dict(row) for row in backup.execute('SELECT * FROM vocabulary')}, before)
      self.assertEqual([tuple(row) for row in backup.execute('SELECT * FROM vocabulary_reviews')], history)
    with database() as connection:
      after = {row['id']: dict(row) for row in connection.execute('SELECT * FROM vocabulary')}
      self.assertEqual([tuple(row) for row in connection.execute('SELECT * FROM vocabulary_reviews')], history)
    for wordId, old in before.items():
      if wordId != card['id']:
        self.assertEqual(after[wordId], old)
      else:
        self.assertEqual({key: value for key, value in after[wordId].items() if key not in CONTENT_FIELDS},
                         {key: value for key, value in old.items() if key not in CONTENT_FIELDS})
        self.assertEqual(after[wordId]['roman'], 'kaa fɛɛ')
    self.assertEqual(updateBuiltinVocabulary(self.path, apply=True)['updated'], 0)

  def test_all_known_snapshots_upgrade_to_current_catalog(self):
    current = {(word['lesson_id'], word['thai']): word for lesson in catalog() for word in lesson['words']}
    # Multiple historical versions can share a Thai key: test each independently.
    for index, word in enumerate(self.legacy):
      path = Path(self.directory.name, f'version-{index}.sqlite3')
      backend.app.config['PROGRESS_DATABASE'] = str(path)
      with database() as connection:
        saveWord(connection, word)
      self.assertEqual(updateBuiltinVocabulary(path, apply=True)['updated'], 1)
      with database() as connection:
        row = connection.execute('SELECT * FROM vocabulary').fetchone()
        for field in CONTENT_FIELDS:
          self.assertEqual(row[field], current[(row['lesson_id'], row['thai'])][field])

  def test_failed_update_rolls_back_every_card_and_keeps_backup(self):
    with database() as connection:
      for word in self.legacy[:2]:
        saveWord(connection, word)
      before = [dict(row) for row in connection.execute('SELECT * FROM vocabulary ORDER BY id')]
      connection.execute('''CREATE TRIGGER reject_second_update BEFORE UPDATE ON vocabulary
        WHEN OLD.id = 2 BEGIN SELECT RAISE(ABORT, 'synthetic storage failure'); END''')
    with self.assertRaises(sqlite3.IntegrityError):
      updateBuiltinVocabulary(self.path, apply=True)
    with database() as connection:
      self.assertEqual([dict(row) for row in connection.execute('SELECT * FROM vocabulary ORDER BY id')], before)
    self.assertEqual(len(list(self.path.parent.glob('*-before-content-*.sqlite3'))), 1)
