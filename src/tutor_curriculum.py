"""Fixed, reviewed beginner examples selected from the authored curriculum.

Review is the project's editorial/user review, not independent native verification.
"""
import copy
import json
import re

from src.curriculum import LESSONS
from src.vocabulary_content import EXAMPLES
from src.tutor_response import RESPONSE_SCHEMA, validateTeaching, parseObject


def entry(key, lessonId, thai):
  lesson = next(item for item in LESSONS if item['id'] == lessonId)
  line = next((item for item in lesson['dialogue'] if item['thai'] == thai), None)
  if line is None:
    line = dict(zip(('thai', 'roman', 'english'), next(value for value in EXAMPLES.values() if value[0] == thai)))
  return dict(id=key, lesson_id=lessonId, thai=line['thai'], english=line['english'], romanization=line['roman'],
              usage=lesson['pattern'], vocabulary=lesson['vocabulary'])


REVIEWED_EXAMPLES = {
  item['id']: item for item in [
    entry('greeting', 'greetings', 'สวัสดีค่ะ คุณชื่ออะไรคะ'),
    entry('introduction', 'greetings', 'ชื่อแอนค่ะ'),
    entry('food-rice', 'food', 'ขอข้าวผัดหนึ่งจาน ไม่เผ็ดนะครับ'),
    entry('food-water', 'food', 'ขอน้ำหนึ่งแก้วครับ'),
    entry('food-coffee', 'food', 'ขอกาแฟหนึ่งแก้วค่ะ'),
    entry('food-thanks', 'food', 'อร่อยครับ ขอบคุณครับ'),
    entry('directions-near', 'directions', 'ห้องน้ำอยู่แถวนี้ค่ะ'),
    entry('directions-far', 'directions', 'ห้องน้ำอยู่ไกลจากที่นี่ค่ะ'),
    entry('directions-left', 'directions', 'ตรงไป แล้วเลี้ยวซ้ายครับ'),
    entry('numbers-twenty', 'numbers', 'ยี่สิบบาทค่ะ'),
    entry('shopping-price', 'shopping', 'สวัสดีค่ะ อันนี้เท่าไหร่คะ'),
    entry('shopping-bag', 'shopping', 'ไม่รับถุงค่ะ ขอบคุณค่ะ'),
    entry('shopping-question', 'shopping', 'เอาอันนี้ค่ะ มีถุงไหมคะ')
  ]
}

# These alternatives are explicitly taught in the reviewed falling-tone guide.
REVIEWED_EXAMPLES['polite-confirmation'] = dict(id='polite-confirmation', lesson_id='speaking-listening',
  thai='ใช่ค่ะ / ใช่ครับ', english='Yes / correct. (Polite feminine / masculine alternatives.)',
  romanization='châi khâ / châi khráp', usage='ใช่ is valid for yes / correct in context. Polite forms: ใช่ค่ะ / ใช่ครับ. Not every yes/no question is answered with ใช่.', vocabulary=[])

# Exact context cues are intentionally narrow. Explicit document/web questions bypass this selection.
CONTEXT_CUES = {
  'greeting': ('greeting', 'say hello', 'hello in thai'),
  'introduction': ('name is ann', 'introduce myself as ann', 'ชื่อแอน'),
  'food-rice': ('fried rice', 'ข้าวผัด'),
  'food-water': ('glass of water', 'order water', 'น้ำหนึ่งแก้ว'),
  'food-coffee': ('coffee', 'กาแฟ'),
  'directions-near': ('nearby restroom', 'restroom is around here', 'ห้องน้ำอยู่แถวนี้'),
  'directions-far': ('far from here', 'ห้องน้ำอยู่ไกล'),
  'directions-left': ('straight, then turn left', 'straight then turn left', 'ตรงไป แล้วเลี้ยวซ้าย'),
  'numbers-twenty': ('twenty baht', '20 baht', 'ยี่สิบบาท'),
  'shopping-price': ('how much is this', 'อันนี้เท่าไหร่'),
  'shopping-bag': ('decline a bag', 'decline an offered bag', 'ไม่รับถุง'),
  'shopping-question': ('do you have a bag', 'มีถุงไหม', 'คะ versus ค่ะ', 'คะ vs ค่ะ'),
  'polite-confirmation': ('polite confirmation', 'say yes politely', 'ใช่ค่ะ', 'ใช่ครับ')
}


def selectReviewed(query, lesson=None):
  lower = query.casefold()
  selected = [REVIEWED_EXAMPLES[key] for key, cues in CONTEXT_CUES.items() if any(cue in lower for cue in cues)]
  if lesson:
    selected = [item for item in selected if item['lesson_id'] == lesson['id']]
    if not selected:
      selected = [item for item in REVIEWED_EXAMPLES.values() if item['lesson_id'] == lesson['id']][:2]
  return speakerStyle(selected, query)[:3]


def speakerStyle(selected, query):
  lower = query.casefold()
  masculine = bool(re.search(r'\b(male|masculine)\b|as a man|use ครับ', lower))
  feminine = bool(re.search(r'\b(female|feminine)\b|as a woman|use ค่ะ', lower))
  # Never force an incompatible fixed speaker style. Unsupported variants remain
  # on the explicitly unreviewed, script-validated generation path.
  if masculine and not feminine:
    selected = [item for item in selected if not item['thai'].endswith(('ค่ะ', 'คะ')) or 'ครับ' in item['thai']]
  if feminine and not masculine:
    selected = [item for item in selected if 'ครับ' not in item['thai'] or 'ค่ะ' in item['thai']]
  return selected


def restaurantContext(query, messages, lesson=None):
  """Resolve short restaurant follow-ups from learner text, never rejected AI text."""
  direct = selectReviewed(query, lesson)
  if direct:
    return direct
  lower = query.casefold()
  learner_turns = [item['content'] for item in messages if item.get('role') == 'user'][-8:]
  context = ' '.join(learner_turns).casefold()
  restaurant = any(term in context for term in ('restaurant', 'ordering food', 'fried rice', 'ข้าวผัด', 'ร้านอาหาร'))
  if not restaurant:
    return []
  if re.search(r'\bwater\b', lower) and 'coconut' not in lower:
    return speakerStyle([REVIEWED_EXAMPLES['food-water']], query)
  if any(term in lower for term in ('ask the price', 'ask for the price', 'how much', 'ราคา')):
    return speakerStyle([REVIEWED_EXAMPLES['shopping-price']], query)
  if any(term in lower for term in ('thank you', 'thanks', 'ขอบคุณ')):
    return speakerStyle([REVIEWED_EXAMPLES['food-thanks']], query)
  if any(term in lower for term in ('pronunciation', 'again', 'repeat', 'say it', 'slower')):
    for earlier in reversed(learner_turns[:-1]):
      selected = selectReviewed(earlier)
      if not selected and re.search(r'\bwater\b', earlier.casefold()):
        selected = [REVIEWED_EXAMPLES['food-water']]
      if selected:
        return speakerStyle(selected, query)
  if any(term in lower for term in ('restaurant', 'ordering food', 'ร้านอาหาร')):
    food = next(item for item in LESSONS if item['id'] == 'food')
    return selectReviewed(query, food)
  return []


def reviewedFallback(examples, pronunciation=True, translations=True):
  """Return only approved lesson content; no failed model text is reused."""
  content = json.dumps(dict(explanation='', example_ids=[item['id'] for item in examples],
                            language_notes=[], reference_titles=[]))
  return parseReviewed(content, examples, pronunciation, translations)


def reviewedSchema(examples, allow_notes=True):
  schema = copy.deepcopy(RESPONSE_SCHEMA)
  schema['required'].remove('examples')
  schema['required'].append('example_ids')
  del schema['properties']['examples']
  schema['properties']['example_ids'] = dict(type='array', minItems=1, maxItems=3, uniqueItems=True,
    items=dict(type='string', enum=[item['id'] for item in examples]))
  if not allow_notes:
    schema['properties']['language_notes']['maxItems'] = 0
    schema['properties']['reference_titles']['maxItems'] = 0
  return schema


def reviewedInstruction(examples, level='Beginner'):
  return (
    'Return only JSON with explanation, example_ids, language_notes and reference_titles. '
    'Select relevant example_ids from the reviewed curriculum below; do not generate replacement Thai, translations '
    'or pronunciation fields for these fixed examples. The server will insert the exact curriculum text. '
    'Keep the explanation short: respond to the learner and invite one practice turn. '
    'Your explanation and any language notes are AI-generated and unreviewed; never call them verified or accurate. '
    'Use empty language_notes/reference_titles unless actually needed. Never invent references. '
    'Other-script quotations must be in explicitly labeled language_notes; explanation uses English/Thai. '
    'Preserve mode, learner preferences and source facts. Curriculum review is not native verification.\n'
    'Reviewed curriculum entries:\n' + json.dumps(examples, ensure_ascii=False) +
    '\nFinal explanation rules: use only the supplied meanings, vocabulary and usage facts. '
    'Do not introduce alternative Thai sentences, new romanization or tone descriptions in explanation/notes. '
    'Refer to the fixed pronunciation guide instead of rewriting it. '
    'Use คะ for feminine questions and ค่ะ for feminine statements; particle style follows the speaker, not the listener. '
    'สิบ means ten, ร้อย means hundred, and ยี่สิบ means twenty. '
    'If the supplied material does not support a claim, acknowledge uncertainty rather than inventing an explanation. '
    + ('Use at most two short English explanation sentences and one practice question; normally leave language_notes/reference_titles empty.'
       if level == 'Beginner' else
       'Use at most two short explanation sentences and one practice question, honoring the level and translation preferences; normally leave language_notes/reference_titles empty.')
  )


def parseReviewed(content, examples, pronunciation=False, translations=True, allow_notes=True):
  value = parseObject(content)
  if not isinstance(value, dict) or set(value) != {'explanation', 'example_ids', 'language_notes', 'reference_titles'}:
    raise ValueError('Expected reviewed example IDs, not invented teaching fields')
  if not allow_notes and (value['language_notes'] != [] or value['reference_titles'] != []):
    from src.tutor_diagnostics import TutorValidationError
    raise TutorValidationError('unexpected_notes', 'language_notes/reference_titles')
  ids = value.pop('example_ids')
  allowed = {item['id']: item for item in examples}
  if (not isinstance(ids, list) or not 1 <= len(ids) <= 3
      or any(not isinstance(key, str) or key not in allowed for key in ids) or len(set(ids)) != len(ids)):
    raise ValueError('Choose distinct IDs from the supplied curriculum')
  selected = [dict(allowed[key]) for key in ids]
  value['examples'] = [{key: item[key] for key in ('thai', 'english', 'romanization')} for item in selected]
  if not pronunciation:
    for example in value['examples']:
      example['romanization'] = ''
  if not translations:
    for example in value['examples']:
      example['english'] = ''
    for source in selected:
      source['usage'] = ''
  return validateTeaching(value, pronunciation), selected
