"""Safe, request-local diagnostics: never log prompts, completions or credentials."""
from contextvars import ContextVar
import json
import re
import unicodedata

LAST_OLLAMA_CALL = ContextVar('last_ollama_call', default=None)


class TutorValidationError(ValueError):
  def __init__(self, code, field='response', script=None):
    self.code, self.field, self.script = code, field, script
    super().__init__(f'{code} at {field}')


def modelName(value):
  return value if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9._:/-]{1,120}', value) else 'unreported'


def unexpectedScript(value, allowThai=True, allowLatin=True):
  for char in value:
    name = unicodedata.name(char, '')
    if allowThai and 0x0E00 <= ord(char) <= 0x0E7F:
      continue
    if allowLatin and (name.startswith('LATIN') or 0x0300 <= ord(char) <= 0x036F):
      continue
    if 0x116D0 <= ord(char) <= 0x116FF:
      return 'Myanmar'
    if unicodedata.category(char).startswith(('L', 'M')):
      for prefix, family in [('MYANMAR', 'Myanmar'), ('KHMER', 'Khmer'), ('THAI', 'Thai'),
                             ('LATIN', 'Latin'), ('LAO', 'Lao'), ('CYRILLIC', 'Cyrillic'),
                             ('ARABIC', 'Arabic'), ('CJK', 'Han')]:
        if name.startswith(prefix):
          return family
      return 'Other'
  return 'Other'


def validationDiagnostic(error):
  if isinstance(error, TutorValidationError):
    return error.code, error.field
  if isinstance(error, json.JSONDecodeError):
    return 'malformed_json', 'response'
  known = {
    'Invalid teaching object': ('schema_fields', 'response'),
    'Missing teaching examples': ('missing_examples', 'examples'),
    'Invalid example fields': ('schema_fields', 'examples'),
    'Invalid notes or titles': ('schema_fields', 'language_notes/reference_titles'),
    'Invalid language note': ('schema_fields', 'language_notes'),
    'Invalid language note text': ('unsafe_text', 'language_notes'),
    'Invalid language label': ('schema_field', 'language_notes.language'),
    'Quote labeled Thai contains inappropriate script': ('wrong_script', 'language_notes.quote'),
    'Invalid language-note explanation': ('wrong_script', 'language_notes.explanation'),
    'Invalid reference title': ('schema_field', 'reference_titles'),
    'Expected reviewed example IDs, not invented teaching fields': ('schema_fields', 'example_ids'),
    'Choose distinct IDs from the supplied curriculum': ('invalid_example_ids', 'example_ids')
  }
  return known.get(str(error), ('schema_validation', 'response'))
