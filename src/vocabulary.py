"""Saved vocabulary, auditable SM-2 scheduling, and additive SQLite migrations."""
from datetime import datetime, timedelta, timezone
from math import ceil
import unicodedata
from uuid import UUID
from flask import Blueprint, jsonify, request
from src.learning import database, findLesson
from src.vocabulary_content import CATEGORIES, catalog, lessonWords

vocabulary = Blueprint('vocabulary', __name__)


def today():
  return datetime.now(timezone(timedelta(hours=7))).date()


def migrateVocabulary(connection):
  exists = connection.execute("SELECT 1 FROM sqlite_master WHERE name='schema_migrations'").fetchone()
  if exists and connection.execute('SELECT 1 FROM schema_migrations WHERE version = 1').fetchone():
    return
  # Transactional, additive, and serialized even when the first requests race.
  with connection:
    connection.execute('BEGIN IMMEDIATE')
    connection.execute('''CREATE TABLE IF NOT EXISTS schema_migrations (
      version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS vocabulary (
      id INTEGER PRIMARY KEY, thai_key TEXT NOT NULL UNIQUE, thai TEXT NOT NULL,
      roman TEXT NOT NULL, english TEXT NOT NULL, category TEXT NOT NULL,
      example_thai TEXT NOT NULL, example_roman TEXT NOT NULL, example_english TEXT NOT NULL,
      lesson_id TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      due_on TEXT NOT NULL, repetitions INTEGER NOT NULL DEFAULT 0,
      interval_days INTEGER NOT NULL DEFAULT 0, ease REAL NOT NULL DEFAULT 2.5,
      revision INTEGER NOT NULL DEFAULT 0)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS vocabulary_reviews (
      attempt_id TEXT PRIMARY KEY, word_id INTEGER NOT NULL REFERENCES vocabulary(id),
      quality INTEGER NOT NULL CHECK(quality BETWEEN 0 AND 5),
      reviewed_at TEXT NOT NULL, previous_due TEXT NOT NULL,
      previous_interval INTEGER NOT NULL, previous_ease REAL NOT NULL,
      previous_repetitions INTEGER NOT NULL, previous_revision INTEGER NOT NULL,
      due_on TEXT NOT NULL, interval_days INTEGER NOT NULL, ease REAL NOT NULL,
      repetitions INTEGER NOT NULL, revision INTEGER NOT NULL)''')
    connection.execute('CREATE INDEX IF NOT EXISTS vocabulary_due ON vocabulary(due_on)')
    connection.execute('CREATE INDEX IF NOT EXISTS vocabulary_review_word ON vocabulary_reviews(word_id, reviewed_at)')
    connection.execute('INSERT OR IGNORE INTO schema_migrations(version) VALUES (1)')


def sm2(repetitions, interval, ease, quality):
  """Daily SM-2 variant: all grades update ease; lapses restart at one day."""
  if quality < 3:
    repetitions, interval = 0, 1
  else:
    interval = 1 if repetitions == 0 else 6 if repetitions == 1 else ceil(interval * ease)
    repetitions += 1
  ease = round(max(1.3, ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)), 4)
  return dict(repetitions=repetitions, interval_days=min(interval, 36500), ease=ease)


def vocabularyStats(connection):
  counts = connection.execute('''SELECT COUNT(*) AS total,
    COALESCE(SUM(due_on <= ?), 0) AS due,
    COALESCE(SUM(repetitions >= 3 AND interval_days >= 21), 0) AS mastered FROM vocabulary''',
    (today().isoformat(),)).fetchone()
  reviews = connection.execute('''SELECT COUNT(*) AS reviews,
    COALESCE(SUM(quality >= 3), 0) AS recalled FROM vocabulary_reviews''').fetchone()
  return dict(counts, reviews=reviews['reviews'], recalled=reviews['recalled'],
              accuracy=round(reviews['recalled'] / reviews['reviews'] * 100) if reviews['reviews'] else None)


def saveWord(connection, word):
  key = ' '.join(unicodedata.normalize('NFC', word['thai']).split())
  values = [key] + [word[field].strip() for field in ('thai', 'roman', 'english', 'category',
            'example_thai', 'example_roman', 'example_english')] + [word.get('lesson_id'), today().isoformat()]
  cursor = connection.execute('''INSERT INTO vocabulary
    (thai_key, thai, roman, english, category, example_thai, example_roman, example_english, lesson_id, due_on)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(thai_key) DO NOTHING''', values)
  return dict(connection.execute('SELECT * FROM vocabulary WHERE thai_key = ?', (key,)).fetchone()), cursor.rowcount == 1


@vocabulary.get('/api/vocabulary/catalog')
def vocabularyCatalog():
  return jsonify(categories=CATEGORIES, lessons=catalog())


@vocabulary.get('/api/vocabulary')
def vocabularyList():
  category = request.args.get('category', '')
  due = request.args.get('due', '0')
  if category and category not in CATEGORIES or due not in ('0', '1'):
    return jsonify(error='Choose a valid category and due filter.'), 400
  with database() as connection:
    words = [dict(row) for row in connection.execute('''SELECT * FROM vocabulary
      WHERE (? = '' OR category = ?) AND (? = '0' OR due_on <= ?)
      ORDER BY due_on, id''', (category, category, due, today().isoformat()))]
    return jsonify(words=words, categories=CATEGORIES, stats=vocabularyStats(connection), today=today().isoformat())


@vocabulary.post('/api/vocabulary')
def vocabularySave():
  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify(error='Expected a JSON object.'), 400
  if 'lesson_id' in data:
    lesson = findLesson(data['lesson_id'])
    if lesson is None:
      return jsonify(error='Lesson not found.'), 404
    words = lessonWords(lesson)
    if 'word_index' in data:
      index = data['word_index']
      if type(index) is not int or not 0 <= index < len(words):
        return jsonify(error='Choose a valid lesson word.'), 400
      words = [words[index]]
  else:
    fields = ('thai', 'roman', 'english', 'category', 'example_thai', 'example_roman', 'example_english')
    if any(not isinstance(data.get(field), str) or not data[field].strip()
           or len(data[field]) > 500 for field in fields) or data['category'] not in CATEGORIES:
      return jsonify(error='Provide Thai, romanization, English, a category, and a complete example (up to 500 characters per field).'), 400
    if any(not any('\u0e01' <= character <= '\u0e2e' for character in data[field]) for field in ('thai', 'example_thai')):
      return jsonify(error='The word and example must include Thai script.'), 400
    words = [{field: data[field] for field in fields}]
  with database() as connection:
    saved = [saveWord(connection, word) for word in words]
    return jsonify(words=[row for row, created in saved], added=sum(created for row, created in saved)), 200


@vocabulary.get('/api/vocabulary/<int:word_id>/history')
def vocabularyHistory(word_id):
  with database() as connection:
    if not connection.execute('SELECT id FROM vocabulary WHERE id = ?', (word_id,)).fetchone():
      return jsonify(error='Word not found.'), 404
    rows = [dict(row) for row in connection.execute('''SELECT * FROM vocabulary_reviews
      WHERE word_id = ? ORDER BY revision DESC''', (word_id,))]
    return jsonify(history=rows)


@vocabulary.post('/api/vocabulary/<int:word_id>/review')
def vocabularyReview(word_id):
  data = request.get_json(silent=True)
  if (not isinstance(data, dict) or type(data.get('quality')) is not int or not 0 <= data['quality'] <= 5
      or type(data.get('revision')) is not int or data['revision'] < 0):
    return jsonify(error='Provide a recall quality from 0 to 5 and the current card revision.'), 400
  attempt_id = data.get('attempt_id')
  try:
    if not isinstance(attempt_id, str):
      raise ValueError()
    attempt_id = str(UUID(attempt_id))
  except (ValueError, AttributeError):
    return jsonify(error='A valid review attempt ID is required.'), 400
  with database() as connection:
    connection.execute('BEGIN IMMEDIATE')
    prior = connection.execute('SELECT * FROM vocabulary_reviews WHERE attempt_id = ?', (attempt_id,)).fetchone()
    if prior:
      if (prior['word_id'], prior['quality'], prior['previous_revision']) != (word_id, data['quality'], data['revision']):
        return jsonify(error='Review attempt ID already used for another answer.'), 409
      return jsonify(review=dict(prior), replayed=True)
    row = connection.execute('SELECT * FROM vocabulary WHERE id = ?', (word_id,)).fetchone()
    if row is None:
      return jsonify(error='Word not found.'), 404
    if row['revision'] != data['revision']:
      return jsonify(error='This card was reviewed elsewhere. Refresh your vocabulary before reviewing it again.'), 409
    if row['due_on'] > today().isoformat():
      return jsonify(error='This card is not due yet. Browse it without changing its schedule.'), 409
    state = sm2(row['repetitions'], row['interval_days'], row['ease'], data['quality'])
    due = (today() + timedelta(days=state['interval_days'])).isoformat()
    connection.execute('''UPDATE vocabulary SET repetitions = ?, interval_days = ?, ease = ?,
      due_on = ?, revision = revision + 1 WHERE id = ?''',
      (state['repetitions'], state['interval_days'], state['ease'], due, word_id))
    connection.execute('''INSERT INTO vocabulary_reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
      (attempt_id, word_id, data['quality'], datetime.now(timezone.utc).isoformat(), row['due_on'],
       row['interval_days'], row['ease'], row['repetitions'], row['revision'], due,
       state['interval_days'], state['ease'], state['repetitions'], row['revision'] + 1))
    review = dict(connection.execute('SELECT * FROM vocabulary_reviews WHERE attempt_id = ?', (attempt_id,)).fetchone())
    return jsonify(review=review, replayed=False)
