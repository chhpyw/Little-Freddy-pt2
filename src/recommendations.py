"""Deterministic recommendations from saved activity; no invented learner history."""
from src.curriculum import LESSONS
from src.speech_content import SPEECH_ITEMS


def recommendations(connection, lessons, vocabulary):
  suggestions = []
  suggestedLessons = set()
  if vocabulary['due']:
    suggestions.append(dict(title=f"Review {vocabulary['due']} due word(s)",
                            reason='These saved words are due under your spaced repetition schedule.', href='#vocabulary/review'))
  lessonRows = {row['lesson_id']: row for row in lessons}
  for lesson in LESSONS:
    row = lessonRows.get(lesson['id'])
    if row and row['latest_score'] < 75:
      suggestions.append(dict(title='Revisit ' + lesson['title'],
                              reason=f"Your latest quiz score was {row['latest_score']}%. Revisit the examples before retrying.",
                              href='#learn/' + lesson['id']))
      suggestedLessons.add(lesson['id'])
  forgotten = connection.execute('''SELECT DISTINCT v.lesson_id FROM vocabulary v
    JOIN vocabulary_reviews r ON r.word_id = v.id AND r.revision = v.revision
    WHERE r.quality < 3 AND v.lesson_id IS NOT NULL''').fetchall()
  personalMistakes = connection.execute("""SELECT COUNT(*) FROM vocabulary v
    JOIN vocabulary_reviews r ON r.word_id = v.id AND r.revision = v.revision
    WHERE r.quality < 3 AND v.lesson_id IS NULL""").fetchone()[0]
  if personalMistakes:
    suggestions.append(dict(title='Revisit difficult personal words',
                            reason=f'{personalMistakes} personal word(s) were not recalled on their latest review. Browse their examples; scheduled reviews remain due on their saved dates.',
                            href='#vocabulary'))
  for row in forgotten:
    lesson = next((lesson for lesson in LESSONS if lesson['id'] == row['lesson_id']), None)
    if lesson and lesson['id'] not in suggestedLessons:
      suggestions.append(dict(title='Practice ' + lesson['title'],
                              reason='A word saved from this lesson was not recalled on its latest review.',
                              href='#learn/' + lesson['id']))
      suggestedLessons.add(lesson['id'])
  for lesson in LESSONS:
    if not lessonRows.get(lesson['id'], {}).get('completed') and lesson['id'] not in suggestedLessons:
      suggestions.append(dict(title='Continue ' + lesson['title'], reason='This lesson is not completed yet.', href='#learn/' + lesson['id']))
      break
  speech = connection.execute('''SELECT item_id, mode, matched FROM speech_attempts
    WHERE rowid IN (SELECT MAX(rowid) FROM speech_attempts GROUP BY item_id, mode)
    ORDER BY rowid DESC''').fetchall()
  mistake = next((row for row in speech if not row['matched']), None)
  if mistake:
    item = next((item for item in SPEECH_ITEMS if item['id'] == mistake['item_id']), None)
    if item:
      suggestions.append(dict(title='Retry ' + item['topic'],
                              reason='Your latest listening answer or speech transcript did not match the target.',
                              href=f"#speaking/{item['id']}/{mistake['mode']}"))
  else:
    complete = {(row['item_id'], row['mode']) for row in connection.execute(
      'SELECT item_id, mode FROM speech_attempts WHERE matched = 1')}
    missing = next(((item, mode) for item in SPEECH_ITEMS for mode in ('listening', 'speaking')
                    if (item['id'], mode) not in complete), None)
    if missing:
      item, mode = missing
      suggestions.append(dict(title='Try ' + item['topic'] + ' · ' + mode,
                              reason='This activity is not completed yet. Speaking compares transcripts only.',
                              href=f"#speaking/{item['id']}/{mode}"))
  if vocabulary['total'] == 0:
    suggestions.append(dict(title='Build your word collection', reason='No saved words yet. Save lesson vocabulary or add a personal word.', href='#vocabulary'))
  elif not vocabulary['due']:
    nextDue = connection.execute('SELECT MIN(due_on) FROM vocabulary').fetchone()[0]
    suggestions.append(dict(title='Browse your saved words', reason='Your next scheduled review is ' + nextDue + '.', href='#vocabulary'))
  if not suggestions:
    suggestions.append(dict(title='Keep practicing Thai', reason='All current activities are completed. Browse a lesson or practice with your tutor.', href='#tutor'))
  return suggestions[:6]
