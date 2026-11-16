"""Text-only listening and transcription assessment; never analyzes audio or pitch."""
import unicodedata
from uuid import UUID
from flask import Blueprint, jsonify, request
from src.learning import database
from src.speech_content import SPEECH_ITEMS, TONE_GUIDE, TONE_SOURCE

speechPractice = Blueprint('speechPractice', __name__)


def transcriptKey(text):
  # Recognizers vary in spaces and punctuation. Preserve all Thai letters and marks.
  text = unicodedata.normalize('NFC', text).casefold()
  return ''.join(character for character in text
                 if not character.isspace() and not unicodedata.category(character).startswith('P'))


def speechSummary(connection):
  rows = [dict(row) for row in connection.execute('''SELECT item_id, mode,
    COUNT(*) AS attempts, MAX(matched) AS completed FROM speech_attempts GROUP BY item_id, mode''')]
  return dict(items=rows, attempts=sum(row['attempts'] for row in rows),
              completed=sum(row['completed'] for row in rows), total=len(SPEECH_ITEMS) * 2)


@speechPractice.get('/api/speech')
def speechContent():
  return jsonify(tones=TONE_GUIDE, source=TONE_SOURCE,
                 items=[{key: value for key, value in item.items() if key != 'answer'} for item in SPEECH_ITEMS])


@speechPractice.get('/api/speech/progress')
def speechProgress():
  with database() as connection:
    return jsonify(speechSummary(connection))


@speechPractice.post('/api/speech/attempts')
def speechAttempt():
  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify(error='Expected a JSON object.'), 400
  item = next((item for item in SPEECH_ITEMS if item['id'] == data.get('item_id')), None)
  mode = data.get('mode')
  value = data.get('response')
  attempt_id = data.get('attempt_id')
  if item is None or mode not in ('listening', 'speaking'):
    return jsonify(error='Choose a valid practice item and mode.'), 400
  if not isinstance(value, str) or not value.strip() or len(value) > 300:
    return jsonify(error='A nonempty answer or recognized Thai transcript is required (up to 300 characters).'), 400
  try:
    if not isinstance(attempt_id, str):
      raise ValueError()
    attempt_id = str(UUID(attempt_id))
  except (ValueError, AttributeError):
    return jsonify(error='A valid attempt ID is required.'), 400
  if mode == 'listening' and value not in item['options']:
    return jsonify(error='Choose one of the available answers.'), 400
  expected = item['thai'] if mode == 'speaking' else item['answer']
  matched = transcriptKey(value) == transcriptKey(expected)
  with database() as connection:
    connection.execute('BEGIN IMMEDIATE')
    previous = connection.execute('SELECT * FROM speech_attempts WHERE attempt_id = ?', (attempt_id,)).fetchone()
    if previous and (previous['item_id'], previous['mode'], previous['response']) != (item['id'], mode, value):
      return jsonify(error='This attempt ID has already been used.'), 409
    connection.execute('''INSERT OR IGNORE INTO speech_attempts
      (attempt_id, item_id, mode, response, matched) VALUES (?, ?, ?, ?, ?)''',
      (attempt_id, item['id'], mode, value, int(matched)))
  feedback = ('The transcript matches the target text.' if matched else
              'The transcript differs from the target. Listen again and try another short recording.') if mode == 'speaking' else (
              'Correct listening answer.' if matched else 'Listen again and compare the answer shown below.')
  return jsonify(matched=matched, expected=expected, recognized=value if mode == 'speaking' else None,
                 feedback=feedback, limitation='Text comparison only; no tone or pronunciation accuracy is measured.')
