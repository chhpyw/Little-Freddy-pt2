"""Speech practice uses text comparisons, isolated SQLite, and no audio/model services."""
import os
import sqlite3
import tempfile
import unittest
from uuid import uuid4
import app as backend
from src.speech_content import SPEECH_ITEMS


class SpeechTests(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.previous = backend.app.config['PROGRESS_DATABASE']
    backend.app.config['PROGRESS_DATABASE'] = os.path.join(self.directory.name, 'speech.sqlite3')
    self.client = backend.app.test_client()

  def tearDown(self):
    backend.app.config['PROGRESS_DATABASE'] = self.previous
    self.directory.cleanup()

  def attempt(self, item='greeting', mode='speaking', response='สวัสดีครับ', attempt_id=None):
    return self.client.post('/api/speech/attempts', json=dict(
      item_id=item, mode=mode, response=response, attempt_id=attempt_id or str(uuid4())))

  def test_navigation_content_and_five_tones(self):
    page = self.client.get('/')
    self.assertIn(b'href="#speaking"', page.data)
    self.assertIn(b'id="speaking"', page.data)
    content = self.client.get('/api/speech').json
    self.assertEqual([tone['id'] for tone in content['tones']], ['mid', 'low', 'falling', 'high', 'rising'])
    self.assertEqual(len(content['items']), 16)
    self.assertIn('seasite.niu.edu', content['source'])
    for tone in content['tones']:
      for key in ('thai', 'roman', 'english', 'explanation', 'contour'):
        self.assertTrue(tone[key])
    for item in content['items']:
      self.assertNotIn('answer', item)
    self.assertEqual({item['id'] for item in content['items'] if not item['id'].startswith('tone-')},
                     {'greeting', 'introduction', 'food', 'shopping', 'directions',
                      'casual-introduction', 'nearby-restroom', 'far-restroom',
                      'bag-decline', 'non-spicy-rice', 'bag-question'})

  def test_transcript_feedback_ignores_spaces_but_preserves_thai_marks(self):
    result = self.attempt(response=' สวัสดี ครับ! ').json
    self.assertTrue(result['matched'])
    self.assertEqual(result['recognized'], ' สวัสดี ครับ! ')
    self.assertEqual(result['expected'], 'สวัสดีครับ')
    self.assertIn('no tone or pronunciation accuracy', result['limitation'])
    result = self.attempt(response='สวัสดีคับ').json
    self.assertFalse(result['matched'])
    self.assertIn('differs', result['feedback'])
    # Thai tone marks must never be discarded in matching.
    self.assertFalse(self.attempt(item='tone-high', response='ซาย').json['matched'])
    result = self.client.get('/api/speech/progress').json
    self.assertEqual((result['attempts'], result['completed'], result['total']), (3, 1, 2 * len(SPEECH_ITEMS)))

  def test_listening_server_assessment_and_idempotent_retry(self):
    attempt_id = str(uuid4())
    for _ in range(2):
      result = self.attempt(item='tone-low', mode='listening', response='Low', attempt_id=attempt_id)
      self.assertEqual(result.status_code, 200)
      self.assertTrue(result.json['matched'])
    self.assertEqual(self.client.get('/api/speech/progress').json['attempts'], 1)
    self.assertEqual(self.attempt(item='tone-low', mode='listening', response='High', attempt_id=attempt_id).status_code, 409)
    result = self.attempt(item='tone-low', mode='listening', response='High').json
    self.assertFalse(result['matched'])
    self.assertEqual(result['expected'], 'Low')
    self.assertEqual(self.client.get('/api/speech/progress').json['completed'], 1)

  def test_all_modes_persist_and_feed_dashboard_without_changing_lessons(self):
    for item in SPEECH_ITEMS:
      self.assertTrue(self.attempt(item=item['id'], mode='listening', response=item['answer']).json['matched'])
      self.assertTrue(self.attempt(item=item['id'], response=item['thai']).json['matched'])
    fresh = backend.app.test_client().get('/api/progress').json
    self.assertEqual((fresh['completed'], fresh['attempts'], fresh['average_score']), (0, 0, 0))
    self.assertEqual((fresh['speech']['completed'], fresh['speech']['attempts']), (2 * len(SPEECH_ITEMS), 2 * len(SPEECH_ITEMS)))
    with sqlite3.connect(backend.app.config['PROGRESS_DATABASE']) as connection:
      self.assertEqual(connection.execute('SELECT COUNT(*) FROM speech_attempts').fetchone()[0], 2 * len(SPEECH_ITEMS))
    self.assertEqual(backend.app.test_client().get('/api/speech/progress').json['completed'], 2 * len(SPEECH_ITEMS))

  def test_additive_schema_preserves_existing_lesson_database(self):
    with sqlite3.connect(backend.app.config['PROGRESS_DATABASE']) as connection:
      connection.execute('''CREATE TABLE progress (lesson_id TEXT PRIMARY KEY, best_score INTEGER,
        latest_score INTEGER, attempts INTEGER, completed INTEGER, updated_at TEXT)''')
      connection.execute("INSERT INTO progress VALUES ('greetings', 100, 100, 1, 1, '2026-11-13')")
    self.attempt()
    result = self.client.get('/api/progress').json
    self.assertEqual(result['completed'], 1)
    self.assertEqual(result['average_score'], 100)
    self.assertEqual(result['speech']['completed'], 1)

  def test_invalid_attempts_do_not_modify_progress(self):
    valid = dict(item_id='greeting', mode='speaking', response='สวัสดี', attempt_id=str(uuid4()))
    for body in [None, [], {}, dict(valid, item_id='missing'), dict(valid, mode='tone-score'),
                 dict(valid, response=''), dict(valid, response=' '), dict(valid, response=['สวัสดี']),
                 dict(valid, response='a' * 301), dict(valid, attempt_id='invalid'),
                 dict(valid, attempt_id=None), dict(valid, mode='listening', response='invented')]:
      self.assertEqual(self.client.post('/api/speech/attempts', json=body).status_code, 400)
    self.assertEqual(self.client.get('/api/speech/progress').json['attempts'], 0)
