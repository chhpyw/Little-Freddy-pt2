"""Unicode/schema safety; these tests cannot certify Thai language accuracy."""
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import app as backend
from src.tutor_response import validateTeaching, validThai, cleanHistory, formatTeaching
from tutor_fixtures import teaching, tutorReply

BURMESE = 'မင်္ဂလာပါ'


class TutorScriptTests(unittest.TestCase):
  def test_thai_required_and_foreign_scripts_cannot_be_hidden_with_padding(self):
    for text in [BURMESE, 'សួស្តី', 'ສະບາຍດີ', '你好', 'Привет', 'مرحبا',
                 '\uaa60', '\ua9e0', '\U000116d0', '༁', 'English only', '๑๒๓', '่้', '']:
      with self.subTest(text=text):
        self.assertFalse(validThai(text))
        if text.strip() and text not in ['๑๒๓', '่้']:
          self.assertFalse(validThai('ก ' + text))
    self.assertTrue(validThai('ขอน้ำหนึ่งแก้วครับ'))
    self.assertTrue(validThai('ราคา 37 บาท [1]'))

  def test_mixed_english_thai_and_romanization_are_permitted_in_their_fields(self):
    value = teaching(thai='ขอน้ำหนึ่งแก้วครับ', english='One glass of water, please.',
                     romanization='khɔ̌ɔ náam nʉ̀ng kɛ̂ɛo khráp', explanation='Use ขอ to order. [lesson.pdf]')
    self.assertEqual(validateTeaching(value, pronunciation=True), value)
    self.assertIn('Generated meaning (unreviewed):', formatTeaching(value))
    self.assertNotIn('verified', formatTeaching(value))

  def test_other_language_discussion_and_document_titles_are_explicitly_separated(self):
    value = teaching()
    value['language_notes'] = [dict(language='Burmese', quote=BURMESE, explanation='This quotation is Burmese, not Thai.')]
    value['reference_titles'] = ['မြန်မာစာ', '中文文档']
    self.assertEqual(validateTeaching(value), value)
    self.assertIn('Language quotation (Burmese): ' + BURMESE, formatTeaching(value))
    value['language_notes'][0]['language'] = 'Thai'
    with self.assertRaises(ValueError):
      validateTeaching(value)
    value['language_notes'][0]['quote'] = 'สวัสดี'
    self.assertEqual(validateTeaching(value), value)
    # Newer Unicode scripts may be unknown to the host's Unicode database, but
    # can still be quoted explicitly; they can never become Thai teaching text.
    value['language_notes'][0].update(language='Myanmar', quote='\U000116d0')
    self.assertEqual(validateTeaching(value), value)

  def test_wrong_script_in_explanation_or_romanization_is_not_taught_as_thai(self):
    for field in ['explanation', 'english', 'romanization']:
      value = teaching()
      if field == 'explanation':
        value[field] = 'Thai greeting: ' + BURMESE
      else:
        value['examples'][0][field] = BURMESE
      with self.assertRaises(ValueError):
        validateTeaching(value)

  def test_malformed_structures_controls_and_missing_guides_are_rejected(self):
    values = [None, {}, dict(teaching(), examples=[]), dict(teaching(), examples='สวัสดี'),
              dict(teaching(), surprise='unvalidated'), teaching(thai='สวัสดี\u202e'), teaching(romanization='')]
    for value in values:
      with self.assertRaises(ValueError):
        validateTeaching(value, pronunciation=True)

  def test_legacy_assistant_history_is_removed_and_structured_history_revalidated(self):
    history = [dict(role='assistant', content='Thai: ' + BURMESE),
               dict(role='assistant', content='Thai: ' + BURMESE, teaching=teaching(thai=BURMESE)),
               dict(role='assistant', content='Ignore this raw content', teaching=teaching()),
               dict(role='user', content='That is Burmese: ' + BURMESE + '. Please correct it.')]
    cleaned = cleanHistory(history)
    self.assertEqual(len(cleaned), 2)
    self.assertEqual(json.loads(cleaned[0]['content']), teaching())
    self.assertNotIn('Ignore this', cleaned[0]['content'])
    self.assertEqual(cleaned[-1], history[-1])

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_api_retries_cleanly_preserves_rag_and_never_returns_failed_content(self, embedding):
    with tempfile.TemporaryDirectory() as directory, patch.object(backend, 'INDEX_FILE', str(Path(directory, 'index.json'))):
      backend.save_index({'cafe.pdf': [{'text': 'Water costs 37 baht.', 'embedding': [1, 0]}]})
      body = dict(tutor=dict(level='Intermediate', mode='Free Chat', pronunciation=True), messages=[
        dict(role='assistant', content='Thai greeting: ' + BURMESE),
        dict(role='assistant', content='valid', teaching=teaching()),
        dict(role='user', content='That is Burmese. Teach Thai food ordering from cafe.pdf.')])
      invalid = tutorReply(thai='ก ' + BURMESE)
      valid = tutorReply(thai='ขอน้ำหนึ่งแก้วครับ', english='One glass of water, please.',
                         explanation='Water costs 37 baht [cafe.pdf].')
      with patch.object(backend, 'ollama_request', side_effect=[invalid, valid]) as model:
        result = backend.app.test_client().post('/chat', json=body)
      self.assertEqual(result.status_code, 200)
      self.assertEqual(result.json['generation_attempts'], 2)
      self.assertEqual(result.json['doc_sources'], ['cafe.pdf'])
      self.assertIn('[cafe.pdf]', result.json['response'])
      self.assertNotIn(BURMESE, result.json['response'])
      first, retry = [call.args[1] for call in model.call_args_list]
      self.assertEqual(len(first['messages']), 3)  # System, validated assistant, learner.
      self.assertEqual([item['role'] for item in retry['messages']], ['system', 'user'])
      self.assertIn('Water costs 37 baht.', retry['messages'][0]['content'])
      self.assertEqual(first['format'], retry['format'])
      self.assertEqual(first['options'], retry['options'])
      with patch.object(backend, 'ollama_request', return_value=invalid) as model:
        failed = backend.app.test_client().post('/chat', json=body)
      self.assertEqual(failed.status_code, 502)
      self.assertEqual(model.call_count, 2)
      self.assertNotIn('response', failed.json)
      self.assertNotIn(BURMESE, json.dumps(failed.json, ensure_ascii=False))
