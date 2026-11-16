"""Usable reviewed fallback and precise diagnostics without weakening script checks."""
import json
import unittest
from unittest.mock import patch

import requests
import app as backend
from src.tutor_curriculum import restaurantContext, reviewedSchema, REVIEWED_EXAMPLES, parseReviewed
from src.tutor_diagnostics import validationDiagnostic
from src.tutor_response import parseTeaching, tutorHistory
from tutor_fixtures import reviewedReply, teaching


class TutorRecoveryTests(unittest.TestCase):
  def setUp(self):
    self.client = backend.app.test_client()
    self.index = patch.object(backend, 'load_index', return_value={})
    self.index.start()

  def tearDown(self):
    self.index.stop()

  def post(self, content, **extra):
    return self.client.post('/chat', json=dict(messages=[dict(role='user', content=content)],
      tutor=dict(level='Beginner', mode='Roleplay', pronunciation=True), **extra))

  def test_timeout_is_not_a_language_error_and_reviewed_fallback_is_pure(self):
    with patch.object(backend.requests, 'post', side_effect=requests.ReadTimeout('PRIVATE_TIMEOUT_DETAIL')) as request:
      with self.assertLogs(backend.app.logger, level='INFO') as logs:
        result = self.post('Teach me to order fried rice. PRIVATE_LEARNER_TEXT')
    self.assertEqual(request.call_count, 1)  # Do not wait for a second timeout.
    self.assertEqual(result.status_code, 200)
    self.assertEqual(result.json['fallback_reason'], 'timeout')
    self.assertEqual(result.json['response_kind'], 'reviewed_fallback')
    self.assertFalse(result.json['ai_commentary_accepted'])
    self.assertEqual(result.json['teaching']['explanation'], '')
    self.assertEqual(result.json['teaching']['examples'][0]['thai'], REVIEWED_EXAMPLES['food-rice']['thai'])
    self.assertIn('timed out', result.json['warnings'][-1])
    self.assertNotIn('PRIVATE_', '\n'.join(logs.output))
    self.assertNotIn('PRIVATE_', json.dumps(result.json))
    self.assertIn('"kind": "timeout"', '\n'.join(logs.output))
    with patch.object(backend.requests, 'post', side_effect=requests.ReadTimeout()):
      unsupported = self.post('Discuss an advanced scientific discovery.')
    self.assertEqual(unsupported.status_code, 504)
    self.assertEqual(unsupported.json['code'], 'ollama_timeout')
    self.assertNotIn('teaching', unsupported.json)

  def test_malformed_generation_keeps_exact_reviewed_content_after_bounded_retry(self):
    with patch.object(backend, 'ollama_request', return_value={'message': {'content': '{ PRIVATE_COMPLETION'}}) as model:
      with self.assertLogs(backend.app.logger, level='INFO') as logs:
        result = self.post('Teach me ordering fried rice.')
    self.assertEqual(model.call_count, 2)
    self.assertEqual(result.json['fallback_reason'], 'malformed_json')
    self.assertEqual(result.json['generation_attempts'], 2)
    self.assertNotIn('PRIVATE_COMPLETION', result.json['response'])
    self.assertNotIn('PRIVATE_COMPLETION', '\n'.join(logs.output))
    self.assertIn('"reason": "malformed_json"', '\n'.join(logs.output))
    self.assertEqual(result.headers['X-Freddy-Chat-Model'], backend.CHAT_MODEL)
    self.assertEqual(result.headers['X-Freddy-Tutor-Contract'], 'thai-fields-v1')

  def test_precise_script_missing_thai_and_missing_guide_reasons(self):
    cases = [
      (teaching(thai='မင်္ဂလာပါ'), 'wrong_script', 'examples[0].thai'),
      (teaching(thai='Hello'), 'missing_thai', 'examples[0].thai'),
      (teaching(romanization=''), 'missing_romanization', 'examples[0].romanization')]
    for value, reason, field in cases:
      with self.assertRaises(ValueError) as caught:
        parseTeaching(json.dumps(value, ensure_ascii=False), True)
      self.assertEqual(validationDiagnostic(caught.exception), (reason, field))
    good = teaching(explanation='English explanation with a Thai example is allowed.')
    self.assertEqual(parseTeaching(json.dumps(good), True), good)
    fenced = '```json\n' + json.dumps(good) + '\n```'
    self.assertEqual(parseTeaching(fenced, True), good)
    with self.assertRaises(ValueError):
      parseTeaching('untrusted prose ' + fenced, True)

  def test_restaurant_followups_use_learner_context_not_rejected_ai(self):
    history = [dict(role='user', content="Let's practice ordering food at a restaurant.")]
    self.assertTrue(restaurantContext(history[-1]['content'], history))
    history.append(dict(role='user', content='Can I add one glass of water?'))
    history.append(dict(role='user', content='Show the pronunciation again.'))
    self.assertEqual(restaurantContext(history[-1]['content'], history)[0]['id'], 'food-water')
    self.assertEqual(restaurantContext('How do I ask the price?', history)[0]['id'], 'shopping-price')
    self.assertEqual(restaurantContext('How do I say thank you?', history)[0]['id'], 'food-thanks')
    self.assertEqual(restaurantContext('Tell me about space exploration.', history), [])
    self.assertEqual(restaurantContext('Water as a female speaker.', history), [])

  def test_reviewed_schema_notes_and_history_are_bounded_without_discarding_latest_request(self):
    selected = [REVIEWED_EXAMPLES['food-rice']]
    self.assertEqual(reviewedSchema(selected, allow_notes=False)['properties']['language_notes']['maxItems'], 0)
    content = json.loads(reviewedReply('food-rice')['message']['content'])
    content['reference_titles'] = ['invented.pdf']
    with self.assertRaises(ValueError):
      parseReviewed(json.dumps(content), selected, True, allow_notes=False)
    messages = [dict(role='user', content='earlier ' * 1000)]
    messages += [dict(role='assistant', content='raw untrusted', teaching=teaching()), dict(role='user', content='latest learner request')]
    history = tutorHistory(messages, reviewed=True)
    self.assertEqual(history[-1]['content'], 'latest learner request')
    self.assertNotIn('raw untrusted', json.dumps(history))
    self.assertNotIn('"examples"', history[0]['content'])
    self.assertLessEqual(sum(len(item['content']) for item in history), 4500)

  def test_unexpected_actual_model_is_not_accepted_as_the_configured_model(self):
    response = unittest.mock.Mock(status_code=200)
    response.json.return_value = dict(model='unexpected:1b', message=dict(content=reviewedReply('food-rice')['message']['content']))
    with patch.object(backend.requests, 'post', return_value=response):
      result = self.post('Teach fried rice ordering.')
    self.assertEqual(result.json['fallback_reason'], 'model_mismatch')
    self.assertFalse(result.json['ai_commentary_accepted'])
