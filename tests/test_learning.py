"""Learning APIs use temporary SQLite files and mocked local-model calls."""
import os
import tempfile
import unittest
from unittest.mock import patch

import app as backend
from src.curriculum import LESSONS


class LearningTests(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.previous = backend.app.config['PROGRESS_DATABASE']
    backend.app.config['PROGRESS_DATABASE'] = os.path.join(self.directory.name, 'progress.sqlite3')
    self.client = backend.app.test_client()

  def tearDown(self):
    backend.app.config['PROGRESS_DATABASE'] = self.previous
    self.directory.cleanup()

  def submit(self, lesson, answers):
    return self.client.post('/api/lessons/' + lesson['id'] + '/submit', json={'answers': answers})

  def test_curriculum_navigation_and_lesson_content(self):
    curriculum = self.client.get('/api/curriculum').json
    self.assertEqual([course['level'] for course in curriculum['courses']], ['A1', 'A2', 'B1', 'B2'])
    self.assertEqual(len(curriculum['tones']), 5)
    self.assertEqual(len(curriculum['lessons']), 5)
    for lesson in curriculum['lessons']:
      response = self.client.get('/api/lessons/' + lesson['id'])
      self.assertEqual(response.status_code, 200)
      data = response.json
      self.assertTrue(5 <= len(data['vocabulary']) <= 10)
      for field in ['dialogue', 'objectives', 'pattern', 'scenario']:
        self.assertTrue(data[field])
      self.assertEqual({q['type'] for q in data['questions']}, {'choice', 'blank'})
      self.assertTrue(all('answer' not in q and 'alternatives' not in q for q in data['questions']))
    self.assertEqual(self.client.get('/api/lessons/missing').status_code, 404)
    self.assertEqual(self.client.post('/api/lessons/missing/submit', json={}).status_code, 404)

  def test_scoring_threshold_retry_and_persistence(self):
    self.assertEqual(self.client.get('/api/progress').json['completed'], 0)
    lesson = LESSONS[0]
    answers = [question['answer'] for question in lesson['questions']]
    result = self.submit(lesson, answers[:2] + ['wrong', 'wrong']).json
    self.assertEqual(result['score'], 50)
    self.assertFalse(result['passed'])
    self.assertEqual(self.client.get('/api/progress').json['completed'], 0)
    result = self.submit(lesson, answers[:3] + ['wrong']).json
    self.assertEqual(result['score'], 75)
    self.assertTrue(result['passed'])
    self.assertEqual(result['feedback'][-1], {'correct': False, 'answer': answers[-1]})
    self.assertEqual(self.submit(lesson, answers).json['score'], 100)
    self.submit(lesson, ['wrong'] * 4)
    # A new client and connection read persisted rows, with no browser/session state.
    saved = backend.app.test_client().get('/api/progress').json
    self.assertEqual((saved['completed'], saved['percent'], saved['average_score'], saved['attempts']), (1, 20, 100, 4))
    row = saved['lessons'][0]
    self.assertEqual((row['best_score'], row['latest_score'], row['completed']), (100, 0, 1))
    self.assertTrue(os.path.isfile(backend.app.config['PROGRESS_DATABASE']))

  def test_all_lessons_and_romanized_answers(self):
    for lesson in LESSONS:
      answers = [q.get('alternatives', [q['answer']])[0] for q in lesson['questions']]
      answers = ['  ' + answer.upper() + '  ' for answer in answers]
      self.assertEqual(self.submit(lesson, answers).json['score'], 100)
    saved = self.client.get('/api/progress').json
    self.assertEqual((saved['completed'], saved['percent'], saved['attempts']), (5, 100, 5))

  def test_invalid_submission_cannot_change_progress(self):
    for body in [None, [], {}, {'answers': []}, {'answers': ['wrong'] * 3},
                 {'answers': [None] * 4}, {'answers': [' '] * 4}, {'answers': ['x' * 301] * 4}]:
      response = self.client.post('/api/lessons/greetings/submit', json=body)
      self.assertEqual(response.status_code, 400)
    self.assertEqual(self.client.get('/api/progress').json['attempts'], 0)

  @patch.object(backend, 'load_index', return_value={})
  @patch.object(backend, 'get_embedding', return_value=None)
  @patch.object(backend, 'ollama_request', return_value={'message': {'content': 'สวัสดีครับ'}})
  def test_lesson_ai_context_and_validation(self, ollama, embedding, index):
    body = {'messages': [{'role': 'user', 'content': 'สวัสดี'}], 'lesson_id': 'food',
            'translations': False, 'tutor': {'level': 'Beginner', 'mode': 'Roleplay', 'pronunciation': True}}
    self.assertEqual(self.client.post('/chat', json=body).status_code, 200)
    prompt = ollama.call_args.args[1]['messages'][0]['content']
    for expected in ['Ordering food and drinks', 'ข้าว', 'only on request', 'Scenario:']:
      self.assertIn(expected, prompt)
    body['lesson_id'] = 'missing'
    self.assertEqual(self.client.post('/chat', json=body).status_code, 400)
