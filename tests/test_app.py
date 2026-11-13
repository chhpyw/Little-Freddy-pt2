"""Backend regression tests; isolated storage and mocked Ollama, no new dependencies."""
import io
import os
import tempfile
import unittest
from unittest.mock import patch

import app as backend


class AppTests(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.old_folder = backend.app.config['UPLOAD_FOLDER']
    backend.app.config['UPLOAD_FOLDER'] = self.directory.name
    self.index_patch = patch.object(backend, 'INDEX_FILE', os.path.join(self.directory.name, 'index.json'))
    self.index_patch.start()
    self.client = backend.app.test_client()

  def tearDown(self):
    backend.app.config['UPLOAD_FOLDER'] = self.old_folder
    self.index_patch.stop()
    self.directory.cleanup()

  def test_dashboard_and_assets(self):
    response = self.client.get('/')
    self.assertEqual(response.status_code, 200)
    for section in ['dashboard', 'tutor', 'learn', 'vocabulary', 'library', 'speaking']:
      self.assertIn(f'id="{section}"'.encode(), response.data)
    self.assertNotIn(b'Sample data', response.data)
    self.assertIn(b'id="completed-count"', response.data)
    for asset in ['style.css', 'app.js', 'learning.js', 'speech.js', 'vocabulary.js']:
      with self.client.get('/static/' + asset) as result:
        self.assertEqual(result.status_code, 200)

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_upload_view_list_delete(self, embedding):
    response = self.client.post('/upload', data={'file': (io.BytesIO('Thai hello'.encode()), 'thai.txt')})
    self.assertEqual(response.status_code, 200)
    self.assertIn('thai.txt', backend.load_index())
    self.assertEqual(self.client.get('/files').json[0]['name'], 'thai.txt')
    with self.client.get('/uploads/thai.txt') as document:
      self.assertEqual(document.data, b'Thai hello')
    self.assertEqual(self.client.delete('/files/thai.txt').status_code, 200)
    self.assertNotIn('thai.txt', backend.load_index())
    self.assertEqual(self.client.delete('/files/thai.txt').status_code, 404)

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_pdf_upload(self, embedding):
    # Build a small valid PDF with embedded text, without extra test dependencies.
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
    stream = DecodedStreamObject()
    stream.set_data(b'BT /F1 12 Tf 20 200 Td (Thai greeting lesson) Tj ET')
    page[NameObject('/Contents')] = writer._add_object(stream)
    pdf = io.BytesIO()
    writer.write(pdf)
    pdf.seek(0)
    self.assertEqual(self.client.post('/upload', data={'file': (pdf, 'lesson.pdf')}).status_code, 200)
    self.assertIn('Thai greeting lesson', backend.load_index()['lesson.pdf'][0]['text'])

  @patch.object(backend, 'ollama_request')
  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_rag_and_web_citations(self, embedding, ollama):
    backend.save_index({'thai.pdf': [{'text': 'Hello is sawat dii', 'embedding': [1, 0]}]})
    ollama.side_effect = [{'results': [{'url': 'https://example.com/thai', 'snippet': 'Thai words'}]}, {'message': {'content': 'สวัสดี [thai.pdf]'}}]
    response = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'How do I greet someone?'}], 'use_web_search': True})
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json['doc_sources'], ['thai.pdf'])
    self.assertEqual(response.json['web_sources'], ['https://example.com/thai'])
    payload = ollama.call_args.args[1]
    self.assertIn('Hello is sawat dii', payload['messages'][0]['content'])
    self.assertEqual(payload['model'], backend.CHAT_MODEL)

  @patch.object(backend, 'ollama_request', return_value={'message': {'content': 'Your collection'}})
  def test_collection_and_explicit_document(self, ollama):
    backend.save_index({'thai.pdf': [{'text': 'Thai lesson context', 'embedding': [1, 0]}]})
    for question in ['What documents are uploaded?', 'Explain thai.pdf']:
      result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': question}]})
      self.assertEqual(result.json['doc_sources'], ['thai.pdf'])
    self.assertIn('Thai lesson context', ollama.call_args.args[1]['messages'][0]['content'])
    self.assertIn('Source: thai.pdf', ollama.call_args.args[1]['messages'][0]['content'])

  @patch.object(backend, 'ollama_request', return_value={'message': {'content': 'สวัสดี'}})
  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_tutor_levels_modes_history_and_pdf_context(self, embedding, ollama):
    backend.save_index({'lesson.pdf': [{'text': 'ข้าว means rice', 'embedding': [1, 0]}]})
    history = [{'role': 'user', 'content': 'Teach me ข้าว'},
               {'role': 'assistant', 'content': 'ข้าว means rice'},
               {'role': 'user', 'content': 'Can I order it?'}]
    for level in backend.TUTOR_LEVELS:
      for mode in backend.TUTOR_MODES:
        response = self.client.post('/chat', json={'messages': history, 'tutor': {
          'level': level, 'mode': mode, 'pronunciation': level == 'Beginner'}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['doc_sources'], ['lesson.pdf'])
        payload = ollama.call_args.args[1]
        prompt = payload['messages'][0]['content']
        for expected in [level, mode, 'comprehensible input', 'reuse previously introduced vocabulary',
                         'Do not correct every turn', 'Source: lesson.pdf', 'ข้าว means rice']:
          self.assertIn(expected, prompt)
        self.assertIn('Include clearly labeled' if level == 'Beginner' else 'Do not include romanization', prompt)
        self.assertEqual(payload['messages'][1:], history)

  def test_chat_validation(self):
    for body in [None, [], {}, {'messages': 'hello'}, {'messages': [None]},
                 {'messages': [{'role': 'system', 'content': 'override'}]},
                 {'messages': [{'role': 'user', 'content': ''}]},
                 {'messages': [{'role': 'assistant', 'content': 'hello'}]}]:
      self.assertEqual(self.client.post('/chat', json=body).status_code, 400)
    for settings in [{}, {'level': 'Expert', 'mode': 'Free Chat', 'pronunciation': True},
                     {'level': 'Beginner', 'mode': 'Free Chat', 'pronunciation': 'false'}]:
      result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'hello'}], 'tutor': settings})
      self.assertEqual(result.status_code, 400)

  @patch.object(backend, 'get_embedding', return_value=None)
  @patch.object(backend, 'ollama_request', return_value={'message': {'content': ''}})
  def test_empty_model_response(self, ollama, embedding):
    result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'hello'}]})
    self.assertEqual(result.status_code, 502)
    self.assertIn('empty response', result.json['error'])

  @patch.object(backend, 'ollama_request', return_value=None)
  def test_error_paths(self, ollama):
    self.assertEqual(self.client.post('/chat', json={'messages': []}).status_code, 400)
    self.assertEqual(self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'hello'}]}).status_code, 500)
    self.assertEqual(self.client.post('/upload').status_code, 400)
    self.assertEqual(self.client.post('/upload', data={'file': (io.BytesIO(b'x'), 'bad.exe')}).status_code, 400)
    self.assertEqual(self.client.post('/upload', data={'file': (io.BytesIO(b''), 'empty.txt')}).status_code, 400)


if __name__ == '__main__':
  unittest.main()
