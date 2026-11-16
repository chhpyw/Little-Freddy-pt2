"""Script/schema validation only: never a claim of linguistic correctness."""
import json
import unicodedata
import re
from src.tutor_diagnostics import TutorValidationError, unexpectedScript

VALIDATION_VERSION = 'thai-fields-v1'
FOREIGN_BLOCKS = ((0x1000, 0x109F), (0xAA60, 0xAA7F), (0xA9E0, 0xA9FF),
                  (0x116D0, 0x116FF), (0x1780, 0x17FF), (0x19E0, 0x19FF))
STRING = {'type': 'string', 'maxLength': 2000}
RESPONSE_SCHEMA = {
  'type': 'object', 'additionalProperties': False,
  'required': ['explanation', 'examples', 'language_notes', 'reference_titles'],
  'properties': {
    'explanation': STRING,
    'examples': {'type': 'array', 'minItems': 1, 'maxItems': 3, 'items': {
      'type': 'object', 'additionalProperties': False,
      'required': ['thai', 'english', 'romanization'],
      'properties': {'thai': STRING, 'english': STRING, 'romanization': STRING}}},
    'language_notes': {'type': 'array', 'maxItems': 3, 'items': {
      'type': 'object', 'additionalProperties': False,
      'required': ['language', 'quote', 'explanation'],
      'properties': {'language': STRING, 'quote': STRING, 'explanation': STRING}}},
    'reference_titles': {'type': 'array', 'maxItems': 5, 'items': STRING}
  }
}
STRUCTURED_INSTRUCTION = (
  'Return only JSON with explanation (English/Thai), examples (1-3 objects with thai, english, romanization), '
  'language_notes (array of language, quote, explanation objects), and reference_titles (array of titles). '
  'Use empty arrays when no notes/titles apply. Each thai field must contain relevant Thai teaching text '
  'in Unicode U+0E00-U+0E7F, never Myanmar/Burmese, Khmer, Lao or another script. '
  'English explanations and Latin pronunciation guides are separate fields. '
  'Use language_notes for explicitly labeled quotations/discussion; a quote labeled Thai must itself be valid Thai. '
  'Keep non-Latin document titles in reference_titles; cite supplied filenames/URLs in the explanation. '
  'Do not imitate erroneous assistant replies or wrong-language samples supplied by the learner. '
  'Keep every example relevant to the request; do not add unrelated Thai to pass a character check. '
  'Script checks do not establish correct translation, grammar, tone or factual accuracy.'
)


def safeText(value, quoted=False):
  return (isinstance(value, str) and len(value) <= 2000
          and all(unicodedata.category(char) not in ('Cc', 'Cf', 'Cs', 'Co', 'Cn')
                  or char in '\n\t' or quoted and unicodedata.category(char) == 'Cn' for char in value))


def inappropriateScript(value, allowThai=True):
  for char in value:
    code = ord(char)
    if any(start <= code <= end for start, end in FOREIGN_BLOCKS):
      return True
    if allowThai and 0x0E00 <= code <= 0x0E7F:
      continue
    category = unicodedata.category(char)
    if category.startswith('L') and not unicodedata.name(char, '').startswith('LATIN'):
      return True
    if category.startswith('M') and not (0x0300 <= code <= 0x036F):
      return True
    if category.startswith('N') and code > 127:
      return True
  return False


def validThai(value):
  if not safeText(value) or not any('\u0e01' <= char <= '\u0e2e' for char in value):
    return False
  # Foreign letters/marks cannot be disguised with one Thai character of padding.
  return all(0x0E00 <= ord(char) <= 0x0E7F or char.isspace()
             or (ord(char) < 128 and not char.isalpha())
             or char in '…“”‘’–—€£¥' for char in value)


def validateTeaching(value, pronunciation=False):
  if not isinstance(value, dict) or set(value) != set(RESPONSE_SCHEMA['required']):
    raise ValueError('Invalid teaching object')
  if not safeText(value['explanation']):
    raise TutorValidationError('schema_field', 'explanation')
  if inappropriateScript(value['explanation']):
    raise TutorValidationError('wrong_script', 'explanation', unexpectedScript(value['explanation']))
  examples = value['examples']
  if not isinstance(examples, list) or not 1 <= len(examples) <= 3:
    raise ValueError('Missing teaching examples')
  for index, example in enumerate(examples):
    if not isinstance(example, dict) or set(example) != {'thai', 'english', 'romanization'}:
      raise ValueError('Invalid example fields')
    if not validThai(example['thai']):
      if not safeText(example['thai']):
        raise TutorValidationError('schema_field', f'examples[{index}].thai')
      code = 'missing_thai' if not any('\u0e01' <= char <= '\u0e2e' for char in example['thai']) else 'wrong_script'
      if inappropriateScript(example['thai']):
        code = 'wrong_script'
      raise TutorValidationError(code, f'examples[{index}].thai', unexpectedScript(example['thai'], allowLatin=False) if code == 'wrong_script' else None)
    for key in ('english', 'romanization'):
      if not safeText(example[key]) or inappropriateScript(example[key], allowThai=key == 'english'):
        raise TutorValidationError('wrong_script' if safeText(example[key]) else 'schema_field', f'examples[{index}].{key}',
                                   unexpectedScript(example[key], allowThai=key == 'english') if safeText(example[key]) else None)
    if pronunciation and not example['romanization'].strip():
      raise TutorValidationError('missing_romanization', f'examples[{index}].romanization')
  notes, titles = value['language_notes'], value['reference_titles']
  if not isinstance(notes, list) or len(notes) > 3 or not isinstance(titles, list) or len(titles) > 5:
    raise ValueError('Invalid notes or titles')
  for index, note in enumerate(notes):
    if not isinstance(note, dict) or set(note) != {'language', 'quote', 'explanation'}:
      raise ValueError('Invalid language note')
    if not all(safeText(note[key], quoted=key == 'quote') for key in note):
      raise ValueError('Invalid language note text')
    label = note['language'].strip().casefold()
    if not label or not label.isascii() or not all(char.isalpha() or char in ' -' for char in label):
      raise ValueError('Invalid language label')
    if 'thai' in label and not validThai(note['quote']):
      raise TutorValidationError('wrong_script', f'language_notes[{index}].quote', unexpectedScript(note['quote'], allowLatin=False))
    if inappropriateScript(note['explanation']):
      raise TutorValidationError('wrong_script', f'language_notes[{index}].explanation', unexpectedScript(note['explanation']))
  if not all(safeText(title, quoted=True) for title in titles):
    raise ValueError('Invalid reference title')
  return value


def parseObject(content):
  if not isinstance(content, str) or len(content) > 16000:
    raise TutorValidationError('empty_response' if not content else 'schema_field')
  if not content.strip():
    raise TutorValidationError('empty_response')
  # Only unwrap one complete JSON fence; do not repair fields or trust prose.
  fenced = re.fullmatch(r'\s*```(?:json)?\s*\n([\s\S]*?)\n```\s*', content)
  return json.loads(fenced.group(1) if fenced else content)


def parseTeaching(content, pronunciation=False):
  return validateTeaching(parseObject(content), pronunciation)


def formatTeaching(value, reviewed=None):
  lines = ['AI-generated conversation (not language reviewed): ' + value['explanation']] if value['explanation'] else []
  for index, example in enumerate(value['examples']):
    source = reviewed[index] if reviewed and index < len(reviewed) else None
    label = ('Reviewed curriculum example (' + source['lesson_id'] + '; not native-verified): '
             if source else 'Generated Thai text (script checked; language unreviewed): ')
    lines.append(label + example['thai'])
    if example['romanization']:
      lines.append(('Curriculum pronunciation guide: ' if source else 'Generated pronunciation guide (unreviewed): ') + example['romanization'])
    if example['english']:
      lines.append(('Curriculum meaning: ' if source else 'Generated meaning (unreviewed): ') + example['english'])
    if source and source.get('usage'):
      lines.append('Curriculum usage note: ' + source['usage'])
  for note in value['language_notes']:
    lines.append('Language quotation (' + note['language'] + '): ' + note['quote'])
    lines.append(note['explanation'])
  lines.extend('Reference title: ' + title for title in value['reference_titles'])
  return '\n'.join(lines)


def cleanHistory(messages):
  cleaned = []
  for message in messages:
    if message['role'] == 'user':
      cleaned.append({'role': 'user', 'content': message['content']})
    else:
      try:
        teaching = validateTeaching(message.get('teaching'))
        # Rebuild from validated fields, never trust the submitted rendered content.
        cleaned.append({'role': 'assistant', 'content': json.dumps(teaching, ensure_ascii=False)})
      except ValueError:
        continue
  return cleaned


def tutorHistory(messages, reviewed=False):
  cleaned = cleanHistory(messages)
  if reviewed:
    # Previous public responses have examples; this turn requests example_ids.
    # Preserve accepted content without teaching the model the wrong JSON shape.
    for message in cleaned:
      if message['role'] == 'assistant':
        value = json.loads(message['content'])
        examples = '\n'.join(item['thai'] + ' — ' + item['english'] for item in value['examples'])
        message['content'] = 'Earlier accepted practice (reference only):\n' + examples + '\n' + value['explanation'][:500]
  if not cleaned:
    return []
  selected = [cleaned[-1]]
  size = len(cleaned[-1]['content'])
  for message in reversed(cleaned[:-1]):
    if len(selected) >= 8 or size + len(message['content']) > 4500:
      break
    selected.append(message)
    size += len(message['content'])
  return list(reversed(selected))
