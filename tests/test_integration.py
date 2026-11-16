"""Cross-feature, document integrity, malformed-service, and security regressions."""
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch
from uuid import uuid4
from html.parser import HTMLParser

import app as backend
from tutor_fixtures import tutorReply, teaching


class IntegrationTests(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.original = dict(backend.app.config)
    backend.app.config.update(UPLOAD_FOLDER=self.directory.name,
      PROGRESS_DATABASE=os.path.join(self.directory.name, 'learner.sqlite3'))
    self.indexPatch = patch.object(backend, 'INDEX_FILE', os.path.join(self.directory.name, 'index.json'))
    self.indexPatch.start()
    self.client = backend.app.test_client()

  def tearDown(self):
    backend.app.config.clear()
    backend.app.config.update(self.original)
    self.indexPatch.stop()
    self.directory.cleanup()

  def upload(self, name='thai.txt', data=b'Thai example'):
    return self.client.post('/upload', data={'file': (io.BytesIO(data), name)})

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_duplicate_upload_cannot_replace_existing_file(self, embedding):
    self.assertEqual(self.upload(data=b'original').status_code, 200)
    previous = Path(backend.INDEX_FILE).read_bytes()
    self.assertEqual(self.upload(data=b'replacement').status_code, 409)
    self.assertEqual(Path(self.directory.name, 'thai.txt').read_bytes(), b'original')
    self.assertEqual(Path(backend.INDEX_FILE).read_bytes(), previous)

  @patch.object(backend, 'get_embedding', side_effect=[[1, 0], None])
  def test_partial_embedding_failure_cannot_publish_incomplete_document(self, embedding):
    result = self.upload(data=b'a' * 700)
    self.assertGreaterEqual(result.status_code, 500)
    self.assertNotIn('thai.txt', backend.load_index())
    self.assertFalse(Path(self.directory.name, 'thai.txt').exists())

  def test_failed_extraction_does_not_leave_orphan(self):
    self.assertEqual(self.upload('bad.pdf', b'not a PDF').status_code, 400)
    self.assertFalse(Path(self.directory.name, 'bad.pdf').exists())

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_sanitized_upload_name_must_still_have_allowed_extension(self, embedding):
    self.assertEqual(self.upload('.pdf').status_code, 400)

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_corrupt_index_is_not_silently_replaced(self, embedding):
    Path(backend.INDEX_FILE).write_text('{broken JSON')
    result = self.upload()
    self.assertEqual(result.status_code, 503)
    self.assertEqual(Path(backend.INDEX_FILE).read_text(), '{broken JSON')
    self.assertFalse(Path(self.directory.name, 'thai.txt').exists())

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  @patch.object(backend, 'ollama_request', return_value={'message': {'content': 'A Thai explanation'}})
  def test_mismatched_embedding_dimensions_do_not_crash_retrieval(self, ollama, embedding):
    backend.save_index({'old.txt': [{'text': 'old content', 'embedding': [1, 0, 0]}]})
    result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'hello'}]})
    self.assertEqual(result.status_code, 200)
    self.assertEqual(result.json['doc_sources'], [])

  def test_embedding_validation(self):
    for value in [None, [], 'invalid', [float('nan')], [float('inf')], [[1]], [True], [0, 0], [10**400]]:
      with patch.object(backend, 'ollama_request', return_value={'embedding': value}):
        self.assertIsNone(backend.get_embedding('hello'))
    with patch.object(backend, 'ollama_request', return_value={'embedding': [0.5, 0.2]}):
      self.assertEqual(backend.get_embedding('hello'), [0.5, 0.2])

  @patch.object(backend, 'get_embedding', return_value=None)
  def test_malformed_model_response_returns_controlled_error(self, embedding):
    for value in [[], 'text', {'message': None}, {'message': 'text'}, {'message': {'content': []}}]:
      with patch.object(backend, 'ollama_request', return_value=value):
        result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'hello'}]})
        self.assertGreaterEqual(result.status_code, 500)
        self.assertNotIn('has no attribute', result.json['error'])

  @patch.object(backend, 'get_embedding', return_value=None)
  @patch.object(backend, 'ollama_request', return_value={'message': {'content': 'hello'}})
  def test_boolean_settings_are_validated(self, ollama, embedding):
    for key in ['use_web_search', 'translations']:
      result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'hello'}], key: 'false'})
      self.assertEqual(result.status_code, 400)

  def test_json_size_limit_and_storage_errors(self):
    backend.app.config['MAX_CONTENT_LENGTH'] = 50
    result = self.client.post('/chat', data='x' * 100, content_type='application/json')
    self.assertEqual(result.status_code, 413)
    self.assertTrue(result.is_json)
    backend.app.config['MAX_CONTENT_LENGTH'] = self.original['MAX_CONTENT_LENGTH']
    backend.app.config['PROGRESS_DATABASE'] = os.path.join(self.directory.name, 'missing', 'data.sqlite3')
    result = self.client.get('/api/progress')
    self.assertEqual(result.status_code, 503)
    self.assertTrue(result.is_json)
    self.assertNotIn(self.directory.name, result.json['error'])

  def test_cross_site_mutations_and_host_rebinding_are_rejected(self):
    result = self.client.post('/api/vocabulary', json={'lesson_id': 'food'}, headers={'Origin': 'https://evil.example'})
    self.assertEqual(result.status_code, 403)
    self.assertEqual(self.client.get('/', base_url='http://evil.example').status_code, 400)
    self.assertEqual(self.client.post('/api/vocabulary', json={'lesson_id': 'food'}, headers={'Origin': 'http://localhost'}).status_code, 200)

  def test_document_aliases_and_symlinks_cannot_escape_library(self):
    Path(self.directory.name, 'visible.txt').write_text('safe')
    secret = Path(self.directory.name, 'secret.txt')
    secret.write_text('private')
    Path(self.directory.name, 'linked.txt').symlink_to(secret)
    self.assertEqual(self.client.get('/uploads/linked.txt').status_code, 404)
    self.assertEqual(self.client.delete('/files/linked.txt').status_code, 404)
    self.assertEqual(self.client.delete('/files/..visible.txt').status_code, 400)
    self.assertTrue(Path(self.directory.name, 'visible.txt').exists())
    self.assertTrue(secret.exists())

  def test_security_headers(self):
    result = self.client.get('/')
    self.assertEqual(result.headers.get('X-Content-Type-Options'), 'nosniff')
    self.assertIn("frame-ancestors 'none'", result.headers.get('Content-Security-Policy', ''))

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  @patch.object(backend, 'ollama_request', return_value=tutorReply(explanation='Hello [integration.txt]'))
  def test_end_to_end_feature_flow_uses_isolated_storage(self, ollama, embedding):
    self.assertEqual(self.upload('integration.txt', b'Hello is sawat dii.').status_code, 200)
    chat = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'Explain integration.txt'}],
      'tutor': {'level': 'Beginner', 'mode': 'Guided Lesson', 'pronunciation': True}})
    self.assertEqual(chat.json['doc_sources'], ['integration.txt'])
    self.assertIn('Hello is sawat dii.', ollama.call_args.args[1]['messages'][0]['content'])
    for lesson in backend.app.test_client().get('/api/curriculum').json['lessons']:
      from src.curriculum import LESSONS
      actual = next(item for item in LESSONS if item['id'] == lesson['id'])
      answers = [question['answer'] for question in actual['questions']]
      self.assertEqual(self.client.post('/api/lessons/' + lesson['id'] + '/submit', json={'answers': answers}).json['score'], 100)
    words = self.client.post('/api/vocabulary', json={'lesson_id': 'food'}).json['words']
    word = words[0]
    self.assertEqual(self.client.post(f"/api/vocabulary/{word['id']}/review", json=dict(quality=4, revision=0, attempt_id=str(uuid4()))).status_code, 200)
    self.assertEqual(self.client.post('/api/speech/attempts', json=dict(item_id='greeting', mode='speaking', response='สวัสดีครับ', attempt_id=str(uuid4()))).status_code, 200)
    result = backend.app.test_client().get('/api/progress').json
    self.assertEqual((result['completed'], result['percent'], result['average_score']), (5, 100, 100))
    self.assertEqual((result['speech']['completed'], result['vocabulary']['reviews'], result['vocabulary']['due']), (1, 1, 7))
    self.assertEqual(self.client.delete('/files/integration.txt').status_code, 200)
    self.assertNotIn('integration.txt', backend.load_index())

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_docx_and_markdown_extraction(self, embedding):
    from docx import Document
    document = Document(); document.add_paragraph('สวัสดี means hello')
    output = io.BytesIO(); document.save(output)
    self.assertEqual(self.upload('words.docx', output.getvalue()).status_code, 200)
    self.assertIn('สวัสดี', backend.load_index()['words.docx'][0]['text'])
    self.assertEqual(self.upload('notes.md', '# Thai greeting'.encode()).status_code, 200)
    self.assertIn('# Thai greeting', backend.load_index()['notes.md'][0]['text'])

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_index_write_failure_rolls_back_upload_and_delete(self, embedding):
    with patch.object(backend, 'save_index', side_effect=backend.IndexStorageError):
      self.assertEqual(self.upload().status_code, 503)
    self.assertFalse(Path(self.directory.name, 'thai.txt').exists())
    self.assertEqual(self.upload().status_code, 200)
    oldIndex = Path(backend.INDEX_FILE).read_bytes()
    with patch.object(backend, 'save_index', side_effect=backend.IndexStorageError):
      self.assertEqual(self.client.delete('/files/thai.txt').status_code, 503)
    self.assertEqual(Path(self.directory.name, 'thai.txt').read_bytes(), b'Thai example')
    self.assertEqual(Path(backend.INDEX_FILE).read_bytes(), oldIndex)

  @patch.object(backend, 'get_embedding', return_value=[1, 0])
  def test_concurrent_uploads_keep_both_index_entries(self, embedding):
    def upload(name):
      with backend.app.test_client() as client:
        return client.post('/upload', data={'file': (io.BytesIO(b'hello'), name)}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
      self.assertEqual(list(pool.map(upload, ['one.txt', 'two.txt'])), [200, 200])
    self.assertEqual(set(backend.load_index()), {'one.txt', 'two.txt'})

  def test_reindex_retries_transient_failure_and_preserves_other_vectors(self):
    import reindex
    document = Path(self.directory.name, 'thai.txt')
    document.write_text('a' * 700)
    original = document.read_bytes()
    other = [{'text': 'unrelated content', 'embedding': [0, 1]}]
    backend.save_index({'other.txt': other})
    report = []
    with patch.object(backend, 'get_embedding', side_effect=[None, [1, 0], [0, 1]]) as embedding:
      self.assertEqual(reindex.reindex_all(report=report), 1)
    self.assertEqual(embedding.call_count, 3)
    self.assertEqual(backend.load_index()['other.txt'], other)
    self.assertEqual(len(backend.load_index()['thai.txt']), 2)
    self.assertEqual(document.read_bytes(), original)
    self.assertEqual(report[0]['status'], 'indexed')

  def test_reindex_dimension_failure_or_exhausted_retry_keeps_index_bytes(self):
    import reindex
    Path(self.directory.name, 'thai.txt').write_text('a' * 700)
    backend.save_index({'thai.txt': [{'text': 'original', 'embedding': [1, 0]}]})
    original = Path(backend.INDEX_FILE).read_bytes()
    for responses, reason in [([[1, 0], [1, 0, 0]], 'dimensions'), ([None, None], '2 attempt(s)')]:
      report = []
      with patch.object(backend, 'get_embedding', side_effect=responses):
        self.assertEqual(reindex.reindex_all(report=report), 0)
      self.assertIn(reason, report[0]['reason'])
      self.assertEqual(Path(backend.INDEX_FILE).read_bytes(), original)

  def test_reindex_keeps_previous_chunks_on_partial_failure(self):
    import reindex
    Path(self.directory.name, 'thai.txt').write_text('a' * 700)
    previous = {'thai.txt': [{'text': 'previous complete content', 'embedding': [1, 0]}]}
    backend.save_index(previous)
    with patch.object(backend, 'get_embedding', side_effect=[[1, 0], None]):
      self.assertEqual(reindex.reindex_all(max_attempts=1), 0)
    self.assertEqual(backend.load_index(), previous)

  @patch.object(backend, 'get_embedding', return_value=None)
  @patch.object(backend, 'ollama_request', return_value={'message': {'content': 'Hello'}})
  def test_missing_retrieval_and_thai_script_are_disclosed(self, ollama, embedding):
    backend.save_index({'thai.txt': [{'text': 'hello', 'embedding': [1, 0]}]})
    result = self.client.post('/chat', json={'messages': [{'role': 'user', 'content': 'Greet me in Thai'}],
      'tutor': dict(level='Beginner', mode='Free Chat', pronunciation=True)})
    self.assertEqual(result.status_code, 502)
    self.assertEqual(result.json['code'], 'invalid_thai_generation')
    self.assertNotIn('response', result.json)

  def test_gitignore_excludes_private_runtime_files(self):
    paths = ['.venv/private', 'uploads/private.pdf', 'vector_index.json', 'learner.sqlite3',
             'learner.sqlite3-wal', 'learner.sqlite3-shm', 'other.db', '.env', '.env.local', 'credentials-local.json', 'private.key']
    result = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin'], input='\n'.join(paths) + '\n', text=True, capture_output=True, check=False)
    self.assertEqual(result.returncode, 0)
    self.assertEqual(set(result.stdout.splitlines()), set(paths))

  def test_learner_records_survive_a_fresh_python_process(self):
    self.client.post('/api/vocabulary', json={'lesson_id': 'greetings'})
    environment = dict(os.environ, FREDDY_PROGRESS_DATABASE=backend.app.config['PROGRESS_DATABASE'],
      FREDDY_UPLOAD_FOLDER=self.directory.name, FREDDY_INDEX_FILE=backend.INDEX_FILE)
    result = subprocess.run([sys.executable, '-c', "from app import app; print(app.test_client().get('/api/progress').json['vocabulary']['total'])"],
      env=environment, text=True, capture_output=True, timeout=10, check=False)
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(result.stdout.strip(), '8')

  def test_speech_retries_are_canonical_and_atomic(self):
    token = str(uuid4())
    def saveAttempt(response):
      with backend.app.test_client() as client:
        return client.post('/api/speech/attempts', json=dict(item_id='greeting', mode='speaking',
          response=response, attempt_id=token)).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
      self.assertEqual(sorted(pool.map(saveAttempt, ['สวัสดีครับ', 'ขอบคุณครับ'])), [200, 409])
    self.assertEqual(self.client.get('/api/speech/progress').json['attempts'], 1)
    from src.learning import database
    with backend.app.app_context(), database() as connection:
      saved = connection.execute('SELECT response FROM speech_attempts WHERE attempt_id = ?', (token,)).fetchone()['response']
    result = self.client.post('/api/speech/attempts', json=dict(item_id='greeting', mode='speaking', response=saved, attempt_id=token.upper()))
    self.assertEqual(result.status_code, 200)
    self.assertEqual(self.client.get('/api/speech/progress').json['attempts'], 1)

  def test_malformed_web_results_are_filtered(self):
    results = [None, {'url': 'javascript:alert(1)', 'snippet': 'bad'},
      {'url': 'https://[', 'snippet': 'bad'}, {'url': 'https:///missing', 'snippet': 'bad'},
      {'url': 'https://example.com', 'snippet': 'Thai example'}]
    with patch.object(backend, 'ollama_request', return_value={'results': results}):
      self.assertEqual(backend.perform_web_search('Thai'), [results[-1]])

  def test_html_ids_and_local_asset_references(self):
    class Document(HTMLParser):
      def __init__(self):
        super().__init__(); self.ids = []; self.assets = []
      def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'script': self.assets.append(attrs['src'])
    parser = Document(); parser.feed(self.client.get('/').text)
    self.assertEqual(len(parser.ids), len(set(parser.ids)))
    for asset in parser.assets:
      with self.client.get(asset) as response:
        self.assertEqual(response.status_code, 200)
