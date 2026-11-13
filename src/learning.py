"""SQLite progress and server-side assessment for the personal learning space."""
import sqlite3
from contextlib import contextmanager
import unicodedata
from flask import Blueprint, current_app, jsonify, request
from src.curriculum import COURSES, LESSONS, TONES

learning = Blueprint('learning', __name__)


@contextmanager
def database():
  connection = sqlite3.connect(current_app.config['PROGRESS_DATABASE'])
  try:
    connection.row_factory = sqlite3.Row
    connection.execute('''CREATE TABLE IF NOT EXISTS progress (
      lesson_id TEXT PRIMARY KEY, best_score INTEGER NOT NULL,
      latest_score INTEGER NOT NULL, attempts INTEGER NOT NULL,
      completed INTEGER NOT NULL, updated_at TEXT NOT NULL)''')
    connection.execute("""CREATE TABLE IF NOT EXISTS speech_attempts (
      attempt_id TEXT PRIMARY KEY, item_id TEXT NOT NULL, mode TEXT NOT NULL,
      response TEXT NOT NULL, matched INTEGER NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    from src.vocabulary import migrateVocabulary
    migrateVocabulary(connection)
    with connection:
      yield connection
  finally:
    connection.close()


def findLesson(lesson_id):
  return next((item for item in LESSONS if item['id'] == lesson_id), None)


def normalize(value):
  return ' '.join(unicodedata.normalize('NFC', value).casefold().split())


@learning.get('/api/curriculum')
def curriculum():
  summaries = [{key: item[key] for key in ('id', 'title', 'level', 'objectives')} for item in LESSONS]
  return jsonify(courses=COURSES, lessons=summaries, tones=TONES)


@learning.get('/api/lessons/<lesson_id>')
def lessonDetail(lesson_id):
  item = findLesson(lesson_id)
  if item is None:
    return jsonify(error='Lesson not found.'), 404
  public = dict(item)
  public['questions'] = [{key: value for key, value in question.items()
                          if key not in ('answer', 'alternatives')} for question in item['questions']]
  return jsonify(public)


@learning.get('/api/progress')
def progress():
  with database() as connection:
    rows = [dict(row) for row in connection.execute('SELECT * FROM progress')]
    from src.speech_practice import speechSummary
    speech = speechSummary(connection)
    from src.vocabulary import vocabularyStats
    from src.recommendations import recommendations
    words = vocabularyStats(connection)
    suggested = recommendations(connection, rows, words)
  completed = sum(row['completed'] for row in rows)
  return jsonify(lessons=rows, completed=completed, total=len(LESSONS), speech=speech, vocabulary=words, recommendations=suggested,
                 percent=round(completed / len(LESSONS) * 100),
                 average_score=round(sum(row['best_score'] for row in rows) / len(rows)) if rows else 0,
                 attempts=sum(row['attempts'] for row in rows))


@learning.post('/api/lessons/<lesson_id>/submit')
def submit(lesson_id):
  item = findLesson(lesson_id)
  if item is None:
    return jsonify(error='Lesson not found.'), 404
  data = request.get_json(silent=True)
  answers = data.get('answers') if isinstance(data, dict) else None
  if (not isinstance(answers, list) or len(answers) != len(item['questions'])
      or any(not isinstance(answer, str) or not answer.strip() or len(answer) > 300 for answer in answers)):
    return jsonify(error='Answer every question before checking your work.'), 400
  feedback = []
  for answer, question in zip(answers, item['questions']):
    accepted = [question['answer']] + question.get('alternatives', [])
    feedback.append(dict(correct=normalize(answer) in [normalize(value) for value in accepted],
                         answer=question['answer']))
  score = round(sum(result['correct'] for result in feedback) / len(feedback) * 100)
  with database() as connection:
    connection.execute('''INSERT INTO progress VALUES (?, ?, ?, 1, ?, datetime('now'))
      ON CONFLICT(lesson_id) DO UPDATE SET
      best_score = MAX(best_score, excluded.best_score), latest_score = excluded.latest_score,
      attempts = attempts + 1, completed = MAX(completed, excluded.completed), updated_at = excluded.updated_at''',
      (lesson_id, score, score, int(score >= 75)))
  return jsonify(score=score, passed=score >= 75, feedback=feedback)
