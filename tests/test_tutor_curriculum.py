"""Protect fixed curriculum provenance, preferences, routing and model override."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import app as backend
from src.tutor_curriculum import REVIEWED_EXAMPLES, selectReviewed, parseReviewed
from src.tutor_response import formatTeaching
from tutor_fixtures import reviewedReply, tutorReply


class TutorCurriculumTests(unittest.TestCase):
  def test_semantic_goldens_match_curriculum_and_context_selection(self):
    cases = json.loads(Path('tests/tutor_semantic_benchmark.json').read_text())
    self.assertEqual({case['category'] for case in cases}, {'greetings', 'food', 'directions', 'numbers', 'shopping', 'polite speech'})
    for case in cases:
      expected = REVIEWED_EXAMPLES[case['expected_example_id']]
      self.assertEqual({key: expected[key] for key in case['expected']}, case['expected'])
      self.assertIn(expected, selectReviewed(case['prompt']))
      self.assertTrue(case['semantic_checklist'])
    self.assertEqual(selectReviewed('Tell me an advanced story about space exploration.'), [])
    self.assertEqual(selectReviewed('Teach a greeting as a male speaker.'), [])
    self.assertEqual(selectReviewed('Teach fried rice ordering as a female speaker.'), [])

  def test_fixed_fields_are_inserted_by_server_and_cannot_be_replaced_by_model(self):
    selected = selectReviewed('Teach me to order fried rice.')
    content = reviewedReply('food-rice')['message']['content']
    teaching, sources = parseReviewed(content, selected, pronunciation=True)
    self.assertEqual(teaching['examples'][0]['thai'], 'ขอข้าวผัดหนึ่งจาน ไม่เผ็ดนะครับ')
    display = formatTeaching(teaching, sources)
    self.assertIn('Reviewed curriculum example', display)
    self.assertIn('AI-generated conversation (not language reviewed)', display)
    self.assertIn('not native-verified', display)
    for invalid in [reviewedReply('unknown')['message']['content'],
                    tutorReply(thai='ขอให้เป็นข้าว')['message']['content'],
                    reviewedReply('food-rice', explanation='မင်္ဂလာပါ')['message']['content']]:
      with self.assertRaises(ValueError):
        parseReviewed(invalid, selected, True)
    hidden, _ = parseReviewed(content, selected, pronunciation=False, translations=False)
    self.assertEqual((hidden['examples'][0]['english'], hidden['examples'][0]['romanization']), ('', ''))

  @patch.object(backend, 'load_index', return_value={})
  @patch.object(backend, 'get_embedding', return_value=None)
  def test_api_retries_reviewed_ids_and_preserves_free_conversation_path(self, embedding, index):
    client = backend.app.test_client()
    body = dict(messages=[dict(role='user', content='Teach me ordering fried rice.')],
                tutor=dict(level='Beginner', mode='Guided Lesson', pronunciation=True))
    with patch.object(backend, 'ollama_request', side_effect=[reviewedReply('unknown'), reviewedReply('food-rice')]) as model:
      response = client.post('/chat', json=body)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json['generation_attempts'], 2)
    self.assertEqual(response.json['reviewed_examples'][0]['id'], 'food-rice')
    self.assertIn('example_ids', model.call_args.args[1]['format']['properties'])
    body['messages'][0]['content'] = 'Tell me an advanced story about space exploration.'
    with patch.object(backend, 'ollama_request', return_value=tutorReply()) as model:
      response = client.post('/chat', json=body)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json['reviewed_examples'], [])
    self.assertIn('language unreviewed', response.json['response'])
    self.assertIn('examples', model.call_args.args[1]['format']['properties'])
    body['messages'][0]['content'] = 'Teach a greeting.'
    body['tutor']['level'] = 'Advanced'
    with patch.object(backend, 'ollama_request', return_value=reviewedReply('greeting')):
      advanced = client.post('/chat', json=body)
    self.assertEqual(advanced.status_code, 200)
    self.assertEqual(advanced.json['teaching']['examples'][0]['english'], '')

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_explicit_rag_keeps_generated_fields_and_citations(self, embedding):
    with tempfile.TemporaryDirectory() as directory, patch.object(backend, 'INDEX_FILE', str(Path(directory, 'index.json'))):
      backend.save_index({'food.pdf': [{'text': 'Fried rice costs 37 baht.', 'embedding': [1, 0]}]})
      with patch.object(backend, 'ollama_request', return_value=tutorReply(explanation='37 baht [food.pdf]')) as model:
        response = backend.app.test_client().post('/chat', json=dict(
          messages=[dict(role='user', content='What does fried rice cost in food.pdf?')],
          tutor=dict(level='Beginner', mode='Free Chat', pronunciation=True)))
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json['reviewed_examples'], [])
      self.assertEqual(response.json['doc_sources'], ['food.pdf'])
      self.assertIn('37 baht [food.pdf]', response.json['response'])
      self.assertIn('examples', model.call_args.args[1]['format']['properties'])
      # A topic word alone must not divert a semantic document question into a
      # canned coffee lesson when retrieved document context is available.
      with patch.object(backend, 'ollama_request', return_value=tutorReply(explanation='37 baht [food.pdf]')) as model:
        semantic = backend.app.test_client().post('/chat', json=dict(
          messages=[dict(role='user', content='How much does coffee cost at the Bangkok practice cafe?')],
          tutor=dict(level='Beginner', mode='Free Chat', pronunciation=True)))
      self.assertEqual(semantic.status_code, 200)
      self.assertEqual(semantic.json['reviewed_examples'], [])
      self.assertEqual(semantic.json['doc_sources'], ['food.pdf'])

  def test_default_and_environment_override_in_fresh_process(self):
    with tempfile.TemporaryDirectory() as directory:
      environment = dict(os.environ, FREDDY_UPLOAD_FOLDER=directory, FREDDY_PROGRESS_DATABASE=directory + '/learner.sqlite3')
      environment.pop('CHAT_MODEL', None)
      for override, expected in [(None, 'qwen3.5:4b'), ('qwen3:1.7b', 'qwen3:1.7b')]:
        if override:
          environment['CHAT_MODEL'] = override
        result = subprocess.run([sys.executable, '-c', 'import app; print(app.CHAT_MODEL)'],
                                env=environment, capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), expected)
