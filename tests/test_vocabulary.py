"""Vocabulary integration tests use the same SQLite factory as lessons/speech."""
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

import app as backend
from src.vocabulary import sm2


class VocabularyTests(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.previous = backend.app.config['PROGRESS_DATABASE']
    backend.app.config['PROGRESS_DATABASE'] = os.path.join(self.directory.name, 'progress.sqlite3')
    self.client = backend.app.test_client()
    self.day = date(2026, 11, 13)
    self.clock = patch('src.vocabulary.today', side_effect=lambda: self.day)
    self.clock.start()

  def tearDown(self):
    self.clock.stop()
    backend.app.config['PROGRESS_DATABASE'] = self.previous
    self.directory.cleanup()

  def manual(self, **changes):
    body = dict(thai='ขอบคุณ', roman='khɔ̀ɔp khun', english='Thank you', category='Greetings',
                example_thai='ขอบคุณครับ', example_roman='khɔ̀ɔp khun khráp', example_english='Thank you (polite).')
    return dict(body, **changes)

  def save(self, **body):
    return self.client.post('/api/vocabulary', json=body)

  def review(self, word, quality, **changes):
    body = dict(quality=quality, revision=word['revision'], attempt_id=str(uuid4()))
    body.update(changes)
    return self.client.post(f"/api/vocabulary/{word['id']}/review", json=body)

  def words(self):
    return self.client.get('/api/vocabulary').json['words']

  def test_empty_state_and_dashboard(self):
    response = self.client.get('/api/vocabulary').json
    self.assertEqual(response['words'], [])
    self.assertEqual(response['today'], self.day.isoformat())
    self.assertEqual(response['stats'], dict(total=0, due=0, mastered=0, reviews=0, recalled=0, accuracy=None))
    progress = self.client.get('/api/progress').json
    self.assertEqual(progress['vocabulary'], response['stats'])
    self.assertEqual(progress['attempts'], 0)
    self.assertIn('#learn/greetings', [row['href'] for row in progress['recommendations']])
    page = self.client.get('/').data
    self.assertNotIn(b'Sample collection', page)
    self.assertIn(b'id="dashboard-word-due"', page)

  def test_existing_lesson_words_examples_and_all_categories(self):
    catalog = self.client.get('/api/vocabulary/catalog').json
    self.assertEqual(len(catalog['categories']), 6)
    self.assertIn('Daily Conversations', catalog['categories'])
    for lesson in catalog['lessons']:
      for word in lesson['words']:
        self.assertIn(word['thai'], word['example_thai'])
        for key in ['roman', 'english', 'example_roman', 'example_english']:
          self.assertTrue(word[key])
      self.assertEqual(self.save(lesson_id=lesson['id']).json['added'], 8)
    self.assertEqual(len(self.words()), 40)
    self.assertEqual({word['category'] for word in self.words()}, set(catalog['categories']))
    self.assertEqual(self.save(lesson_id='food').json['added'], 0)
    self.assertEqual(self.save(lesson_id='food', word_index=0).json['added'], 0)
    self.assertEqual(self.client.get('/api/vocabulary?category=Food').json['stats']['total'], 40)
    self.assertEqual(len(self.client.get('/api/vocabulary?category=Food').json['words']), 8)

  def test_manual_save_duplicate_keeps_content_and_schedule(self):
    result = self.save(**self.manual())
    self.assertEqual(result.status_code, 200)
    word = result.json['words'][0]
    self.assertEqual(result.json['added'], 1)
    self.review(word, 5)
    again = self.save(**self.manual(thai='  ขอบคุณ  ', english='Different meaning'))
    self.assertEqual(again.json['added'], 0)
    saved = again.json['words'][0]
    self.assertEqual(saved['english'], 'Thank you')
    self.assertEqual((saved['revision'], saved['interval_days']), (1, 1))
    self.assertEqual(self.save(lesson_id='greetings').json['added'], 7)
    saved = next(word for word in self.words() if word['id'] == saved['id'])
    self.assertIsNone(saved['lesson_id'])
    self.assertEqual(saved['revision'], 1)

  def test_sm2_schedule_and_mastery_then_lapse(self):
    word = self.save(**self.manual()).json['words'][0]
    expected = [(5, 1, 1, 2.6), (4, 6, 2, 2.6), (3, 16, 3, 2.46), (5, 40, 4, 2.56)]
    for quality, interval, repetitions, ease in expected:
      result = self.review(word, quality)
      self.assertEqual(result.status_code, 200)
      review = result.json['review']
      self.assertEqual((review['interval_days'], review['repetitions'], review['ease']), (interval, repetitions, ease))
      self.assertEqual(review['due_on'], (self.day + timedelta(days=interval)).isoformat())
      word = self.words()[0]
      self.day += timedelta(days=interval)
    stats = self.client.get('/api/progress').json['vocabulary']
    self.assertEqual((stats['mastered'], stats['reviews'], stats['accuracy']), (1, 4, 100))
    self.review(word, 1)
    word = self.words()[0]
    self.assertEqual((word['repetitions'], word['interval_days'], word['ease']), (0, 1, 2.02))
    self.assertEqual(self.client.get('/api/progress').json['vocabulary']['mastered'], 0)
    for _ in range(4):
      self.day += timedelta(days=1)
      self.review(word, 0)
      word = self.words()[0]
    self.assertEqual(word['ease'], 1.3)
    self.day += timedelta(days=1)
    self.assertEqual(self.review(word, 4).json['review']['interval_days'], 1)

  def test_ceil_and_interval_safety_limit(self):
    self.assertEqual(sm2(2, 6, 2.6, 4)['interval_days'], 16)
    self.assertEqual(sm2(10, 36500, 3, 5)['interval_days'], 36500)
    self.assertEqual(sm2(10, 100, 1.3, 0)['ease'], 1.3)

  def test_due_filter_bangkok_dates_and_overdue_schedule(self):
    word = self.save(**self.manual()).json['words'][0]
    self.assertEqual(len(self.client.get('/api/vocabulary?due=1').json['words']), 1)
    self.day += timedelta(days=10)
    result = self.review(word, 4).json['review']
    self.assertEqual(result['due_on'], (self.day + timedelta(days=1)).isoformat())
    self.assertEqual(self.client.get('/api/vocabulary?due=1').json['words'], [])
    self.day += timedelta(days=1)
    self.assertEqual(len(self.client.get('/api/vocabulary?due=1').json['words']), 1)

  def test_idempotent_retry_and_cross_tab_conflict(self):
    word = self.save(**self.manual()).json['words'][0]
    token = str(uuid4())
    first = self.review(word, 4, attempt_id=token)
    duplicate = self.review(word, 4, attempt_id=token.upper())
    self.assertEqual(duplicate.status_code, 200)
    self.assertTrue(duplicate.json['replayed'])
    self.assertEqual(first.json['review'], duplicate.json['review'])
    self.assertEqual(self.review(word, 5).status_code, 409)
    self.assertEqual(self.review(word, 5, attempt_id=token).status_code, 409)
    fresh = self.words()[0]
    self.assertEqual(self.review(fresh, 4).status_code, 409)  # Not due.
    history = self.client.get(f"/api/vocabulary/{word['id']}/history").json['history']
    self.assertEqual(len(history), 1)
    self.assertEqual((history[0]['previous_revision'], history[0]['revision']), (0, 1))

  def test_review_scoring_dashboard_and_persistence(self):
    saved = self.save(lesson_id='food').json['words']
    self.review(saved[0], 0)
    self.review(saved[1], 3)
    progress = backend.app.test_client().get('/api/progress').json
    self.assertEqual(progress['vocabulary'], dict(total=8, due=6, mastered=0, reviews=2, recalled=1, accuracy=50))
    self.assertEqual((progress['completed'], progress['attempts'], progress['average_score']), (0, 0, 0))
    self.assertEqual(progress['speech']['attempts'], 0)
    self.assertEqual(progress['recommendations'][0]['href'], '#vocabulary/review')
    reasons = ' '.join(row['reason'] for row in progress['recommendations'])
    self.assertIn('not recalled', reasons)
    with sqlite3.connect(backend.app.config['PROGRESS_DATABASE']) as connection:
      self.assertEqual(connection.execute('SELECT COUNT(*) FROM vocabulary_reviews').fetchone()[0], 2)
    self.assertEqual(len(backend.app.test_client().get('/api/vocabulary').json['words']), 8)

  def test_recommendations_follow_real_lesson_and_speech_mistakes(self):
    self.client.post('/api/lessons/numbers/submit', json={'answers': ['wrong'] * 4})
    self.client.post('/api/speech/attempts', json=dict(item_id='shopping', mode='speaking', response='สวัสดี', attempt_id=str(uuid4())))
    suggestions = self.client.get('/api/progress').json['recommendations']
    self.assertIn('#learn/numbers', [row['href'] for row in suggestions])
    self.assertIn('#speaking/shopping/speaking', [row['href'] for row in suggestions])
    self.assertIn('latest quiz score was 0%', ' '.join(row['reason'] for row in suggestions))
    # A later correct activity clears that mistake recommendation.
    self.client.post('/api/speech/attempts', json=dict(item_id='shopping', mode='speaking', response='อันนี้เท่าไหร่คะ', attempt_id=str(uuid4())))
    suggestions = self.client.get('/api/progress').json['recommendations']
    self.assertNotIn('latest listening answer', ' '.join(row['reason'] for row in suggestions))

  def test_safe_migration_of_existing_database(self):
    with sqlite3.connect(backend.app.config['PROGRESS_DATABASE']) as connection:
      connection.execute('CREATE TABLE progress (lesson_id TEXT PRIMARY KEY, best_score INTEGER, latest_score INTEGER, attempts INTEGER, completed INTEGER, updated_at TEXT)')
      connection.execute("INSERT INTO progress VALUES ('greetings', 100, 75, 2, 1, '2026-11-13')")
      connection.execute('CREATE TABLE speech_attempts (attempt_id TEXT PRIMARY KEY, item_id TEXT, mode TEXT, response TEXT, matched INTEGER, created_at TEXT)')
      connection.execute("INSERT INTO speech_attempts VALUES ('legacy', 'greeting', 'speaking', 'สวัสดีครับ', 1, '2026-11-13')")
    word = self.save(**self.manual()).json['words'][0]
    self.review(word, 4)
    for _ in range(3):
      result = self.client.get('/api/progress').json
      self.assertEqual((result['completed'], result['attempts'], result['speech']['attempts'], result['vocabulary']['reviews']), (1, 2, 1, 1))
    with sqlite3.connect(backend.app.config['PROGRESS_DATABASE']) as connection:
      self.assertEqual(connection.execute('SELECT COUNT(*) FROM schema_migrations').fetchone()[0], 1)

  def test_simultaneous_saves_and_reviews_are_serialized(self):
    def saveSameWord(_):
      with backend.app.test_client() as client:
        return client.post('/api/vocabulary', json=self.manual()).json
    with ThreadPoolExecutor(max_workers=2) as pool:
      results = list(pool.map(saveSameWord, range(2)))
    self.assertEqual(sum(result['added'] for result in results), 1)
    word = results[0]['words'][0]
    def reviewSameWord(_):
      with backend.app.test_client() as client:
        return client.post(f"/api/vocabulary/{word['id']}/review", json=dict(
          quality=4, revision=0, attempt_id=str(uuid4()))).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
      statuses = list(pool.map(reviewSameWord, range(2)))
    self.assertEqual(sorted(statuses), [200, 409])
    self.assertEqual(self.client.get('/api/progress').json['vocabulary']['reviews'], 1)

  def test_validation_no_unintended_writes(self):
    for body in [None, [], {}, self.manual(category='Other'), self.manual(thai='hello'), self.manual(example_thai='not Thai'), self.manual(roman=''), self.manual(english='x' * 501), {'lesson_id': 'missing'}, {'lesson_id': 'food', 'word_index': True}, {'lesson_id': 'food', 'word_index': 8}]:
      self.assertIn(self.client.post('/api/vocabulary', json=body).status_code, (400, 404))
    self.assertEqual(self.words(), [])
    word = self.save(**self.manual()).json['words'][0]
    valid = dict(quality=4, revision=0, attempt_id=str(uuid4()))
    for body in [None, [], {}, dict(valid, quality=True), dict(valid, quality=6), dict(valid, quality=-1), dict(valid, quality=3.5), dict(valid, revision=-1), dict(valid, attempt_id='bad')]:
      self.assertEqual(self.client.post(f"/api/vocabulary/{word['id']}/review", json=body).status_code, 400)
    self.assertEqual(self.review(dict(word, id=999), 4).status_code, 404)
    self.assertEqual(self.client.get('/api/vocabulary/999/history').status_code, 404)
    for query in ['category=Other', 'due=bad']:
      self.assertEqual(self.client.get('/api/vocabulary?' + query).status_code, 400)
    self.assertEqual(self.client.get('/api/progress').json['vocabulary']['reviews'], 0)
