"""Enrich the existing lesson vocabulary; do not maintain a second word bank."""
from src.curriculum import LESSONS

CATEGORIES = ['Greetings', 'Food', 'Numbers', 'Transportation', 'Shopping', 'Daily Conversations']
LESSON_CATEGORIES = dict(greetings='Greetings', food='Food', numbers='Numbers',
                         directions='Transportation', shopping='Shopping')
# Examples for words not already illustrated in their lesson's dialogue.
EXAMPLES = {
  'ขอบคุณ': ('ขอบคุณครับ', 'khɔ̀ɔp khun khráp', 'Thank you.'),
  'ฉัน': ('ฉันชื่อแอนค่ะ', 'chǎn chʉ̂ʉ ɛɛn khâ', 'My name is Ann.'),
  'ชื่อ': ('ชื่อแอนค่ะ', 'chʉ̂ʉ ɛɛn khâ', 'My name is Ann. (Casual introduction; pronoun omitted.)'),
  'หนึ่ง': ('หนึ่งบาทครับ', 'nʉ̀ng bàat khráp', 'One baht.'),
  'สอง': ('สองบาทครับ', 'sɔ̌ɔng bàat khráp', 'Two baht.'),
  'สาม': ('สามบาทครับ', 'sǎam bàat khráp', 'Three baht.'),
  'สิบ': ('สิบบาทครับ', 'sìp bàat khráp', 'Ten baht.'),
  'ร้อย': ('หนึ่งร้อยบาทครับ', 'nʉ̀ng rɔ́ɔi bàat khráp', 'One hundred baht.'),
  'กาแฟ': ('ขอกาแฟหนึ่งแก้วค่ะ', 'khɔ̌ɔ kaa fɛɛ nʉ̀ng kɛ̂ɛo khâ', 'One cup of coffee, please.'),
  'เลี้ยวขวา': ('เลี้ยวขวาครับ', 'líao khwǎa khráp', 'Turn right.'),
  'ใกล้': ('ห้องน้ำอยู่แถวนี้ค่ะ', 'hɔ̂ng náam yùu thɛ̌ɛo níi khâ', 'The restroom is around here. (Contextual near expression: แถวนี้ = around here.)'),
  'ไกล': ('ห้องน้ำอยู่ไกลจากที่นี่ค่ะ', 'hɔ̂ng náam yùu klai jàak thîi nîi khâ', 'The restroom is far from here.'),
  'ไม่เอา': ('ไม่เอาค่ะ ขอบคุณค่ะ', 'mâi ao khâ khɔ̀ɔp khun khâ', 'I do not want it, thank you. (Direct general refusal.)'),
  'ถุง': ('ไม่รับถุงค่ะ ขอบคุณค่ะ', 'mâi ráp thǔng khâ khɔ̀ɔp khun khâ', 'I won’t take a bag, thank you.'),
  'อันนั้น': ('เอาอันนั้นค่ะ', 'ao an nán khâ', 'I will take that one.'),
  'ได้': ('ได้ครับ', 'dâai khráp', 'Okay.')
}


def lessonWords(lesson):
  words = []
  for index, word in enumerate(lesson['vocabulary']):
    example = next((line for line in lesson['dialogue'] if word['thai'] in line['thai']), None)
    if word['thai'] in EXAMPLES:
      example = dict(zip(('thai', 'roman', 'english'), EXAMPLES[word['thai']]))
    if example is None:
      raise ValueError('Missing vocabulary example: ' + word['thai'])
    category = LESSON_CATEGORIES[lesson['id']]
    if word['thai'] in ('คุณ', 'ผม', 'ฉัน', 'ชื่อ', 'มี', 'ไหม', 'ได้'):
      category = 'Daily Conversations'
    words.append(dict(word, category=category, example_thai=example['thai'],
                      example_roman=example['roman'], example_english=example['english'],
                      lesson_id=lesson['id'], word_index=index))
  return words


def catalog():
  return [dict(id=lesson['id'], title=lesson['title'], words=lessonWords(lesson)) for lesson in LESSONS]
