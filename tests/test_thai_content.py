"""Language regressions for reviewed teaching examples and backward-compatible quizzes.

These fixtures protect editorial decisions; they do not certify native fluency.
"""
import os
import tempfile
import unittest

import app as backend
from src.curriculum import LESSONS, TONES
from src.speech_content import CONVERSATIONS, TONE_GUIDE
from src.vocabulary_content import catalog


class ThaiContentTests(unittest.TestCase):
  def test_quiz_pronunciation_matches_vocabulary_and_keeps_old_answers(self):
    legacyAnswers = {
      'greetings': ['chue', 'khop khun'], 'numbers': ['baht', 'thao rai'],
      'food': ['kho', 'jan'], 'directions': ['yu thi nai', 'trong pai'],
      'shopping': ['mai', 'an ni']
    }
    with tempfile.TemporaryDirectory() as directory:
      previous = backend.app.config['PROGRESS_DATABASE']
      backend.app.config['PROGRESS_DATABASE'] = os.path.join(directory, 'learner.sqlite3')
      try:
        client = backend.app.test_client()
        for lesson in LESSONS:
          words = {word['thai']: word['roman'] for word in lesson['vocabulary']}
          blanks = [q for q in lesson['questions'] if q['type'] == 'blank']
          for question, oldAnswer in zip(blanks, legacyAnswers[lesson['id']]):
            self.assertEqual(question['prompt'].split(' · Romanization: ')[1], words[question['answer']])
            self.assertIn(oldAnswer, question['alternatives'])
          for useLegacy in (True, False):
            oldAnswers = iter(legacyAnswers[lesson['id']])
            answers = [q['answer'] if q['type'] == 'choice' else
                       next(oldAnswers) if useLegacy else q['alternatives'][0]
                       for q in lesson['questions']]
            self.assertEqual(client.post('/api/lessons/' + lesson['id'] + '/submit',
                                        json={'answers': answers}).json['score'], 100)
        self.assertEqual(client.get('/api/progress').json['completed'], 5)
      finally:
        backend.app.config['PROGRESS_DATABASE'] = previous

  def test_greeting_listening_does_not_mark_a_farewell_sense_wrong(self):
    greeting = next(item for item in CONVERSATIONS if item['id'] == 'greeting')
    # สวัสดี is also used on parting: goodbye is not a safe distractor in isolation.
    self.assertEqual(greeting['english'], 'Hello (polite)')
    self.assertNotIn('Goodbye for now', greeting['options'])
    self.assertIn('Excuse me', greeting['options'])

  def test_food_order_and_generated_flashcard_keep_context(self):
    food = next(lesson for lesson in LESSONS if lesson['id'] == 'food')
    order = food['dialogue'][0]
    self.assertIn('ข้าวผัด', order['thai'])
    self.assertIn('fried rice', order['english'])
    self.assertIn('not spicy', order['english'])
    self.assertIn('khâao phàt', order['roman'])
    cards = next(lesson for lesson in catalog() if lesson['id'] == 'food')['words']
    rice = next(card for card in cards if card['thai'] == 'ข้าว')
    self.assertEqual(rice['example_thai'], order['thai'])
    self.assertEqual(rice['example_english'], order['english'])
    self.assertEqual(next(card for card in cards if card['thai'] == 'กาแฟ')['roman'], 'kaa fɛɛ')
    self.assertEqual(next(card for card in cards if card['thai'] == 'แก้ว')['roman'], 'kɛ̂ɛo')

  def test_direction_tones_and_polite_question_are_distinct(self):
    directions = next(lesson for lesson in LESSONS if lesson['id'] == 'directions')
    words = {word['thai']: word['roman'] for word in directions['vocabulary']}
    self.assertEqual((words['ใกล้'], words['ไกล']), ('klâi', 'klai'))
    question = next(item for item in CONVERSATIONS if item['id'] == 'directions')
    self.assertTrue(question['thai'].endswith('คะ'))
    self.assertTrue(question['roman'].endswith('khá'))
    self.assertIn('lɛ́ɛo', directions['dialogue'][1]['roman'])
    self.assertEqual([(t['title'], t['thai'], t['roman']) for t in TONE_GUIDE], [
      ('Mid', 'ดี', 'dii'), ('Low', 'สี่', 'sìi'), ('Falling', 'ใช่', 'châi'),
      ('High', 'ซ้าย', 'sáai'), ('Rising', 'ขวา', 'khwǎa')])
    self.assertEqual([(t[0], t[1], t[2]) for t in TONES], [
      ('Mid', 'มา', 'maa'), ('Low', 'ข่า', 'khàa'), ('Falling', 'ข้าว', 'khâao'),
      ('High', 'ม้า', 'máa'), ('Rising', 'หมา', 'mǎa')])

  def test_prompt_requires_meaning_accuracy_without_claiming_verification(self):
    for mode in backend.TUTOR_MODES:
      for level in backend.TUTOR_LEVELS:
        prompt = backend.tutor_prompt(dict(level=level, mode=mode, pronunciation=True))
        for instruction in ['same meaning in context', 'correct classifier', 'never claim native verification',
                            'ค่ะ for feminine statements', 'คะ for feminine questions', 'doubled vowels for length']:
          self.assertIn(instruction, prompt)
    prompt = backend.tutor_prompt(dict(level='Intermediate', mode='Free Chat', pronunciation=False))
    self.assertIn('Do not include romanization', prompt)
    self.assertNotIn('doubled vowels for length', prompt)
