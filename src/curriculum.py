"""Ordered, cumulative Thai lessons. Romanization is a pronunciation aid."""
COURSES = [
  {'level': 'A1', 'title': 'Beginner', 'goals': ['Greet people politely', 'Handle prices, meals, directions, and shopping']},
  {'level': 'A2', 'title': 'Elementary', 'goals': ['Talk about daily routines and time', 'Arrange transport and accommodation', 'Describe completed actions and changed situations with แล้ว (not a general past-tense marker)']},
  {'level': 'B1', 'title': 'Intermediate', 'goals': ['Tell connected stories', 'Explain health needs and solve travel problems', 'Give reasons using เพราะ and discuss plans']},
  {'level': 'B2', 'title': 'Advanced', 'goals': ['Discuss current affairs and viewpoints', 'Use formal and informal registers appropriately', 'Support an opinion and negotiate solutions']}
]


def lesson(key, title, objectives, words, dialogue, pattern, scenario, questions):
  return dict(id=key, level='A1', title=title, objectives=objectives,
              vocabulary=[dict(zip(('thai', 'roman', 'english'), word)) for word in words],
              dialogue=[dict(zip(('thai', 'roman', 'english'), line)) for line in dialogue],
              pattern=pattern, scenario=scenario, questions=questions)


def mc(prompt, options, answer):
  return dict(type='choice', prompt=prompt, options=options, answer=answer)


def blank(prompt, answer, roman, *legacy):
  # Display the same pronunciation convention as the lesson; keep old input aliases.
  return dict(type='blank', prompt=prompt + ' · Romanization: ' + roman, answer=answer, alternatives=[roman, *legacy])


LESSONS = [
  lesson('greetings', 'Greetings and introductions', ['Say hello and thank you', 'Introduce yourself and ask a name', 'Choose a polite particle'], [
    ('สวัสดี', 'sà wàt dii', 'Hello'), ('ขอบคุณ', 'khɔ̀ɔp khun', 'Thank you'),
    ('ครับ', 'khráp', 'Polite particle, commonly used by men'), ('ค่ะ', 'khâ', 'Polite statement particle, commonly used by women'),
    ('ชื่อ', 'chʉ̂ʉ', 'Name / be named'), ('คุณ', 'khun', 'You (polite / neutral)'), ('ผม', 'phǒm', 'I, commonly used by men in polite speech'), ('ฉัน', 'chǎn', 'I (familiar; often used by women)')], [
    ('สวัสดีครับ ผมชื่อเฟรดดี้', 'sà wàt dii khráp phǒm chʉ̂ʉ Freddy', 'Hello. My name is Freddy.'),
    ('สวัสดีค่ะ คุณชื่ออะไรคะ', 'sà wàt dii khâ khun chʉ̂ʉ à rai khá', 'Hello. What is your name?'),
    ('ผมชื่อเฟรดดี้ครับ', 'phǒm chʉ̂ʉ Freddy khráp', 'My name is Freddy.')],
    'ผม / ฉัน + ชื่อ + name = My name is … . คุณชื่ออะไร = What is your name? ฉัน is familiar; ดิฉัน is a more formal feminine option. ครับ can end statements or questions; use ค่ะ for statements and คะ for questions in the feminine polite style.',
    'Meet a new neighbor. Greet them, exchange names, and thank them.', [
      mc('Which phrase means hello?', ['สวัสดี', 'ขอบคุณ', 'ชื่อ'], 'สวัสดี'),
      mc('Which particle commonly makes a woman’s statement polite?', ['ค่ะ', 'คุณ', 'ผม'], 'ค่ะ'),
      blank('ผม ___ เฟรดดี้ (My name is Freddy)', 'ชื่อ', 'chʉ̂ʉ', 'chue'),
      blank('___ ครับ (Thank you)', 'ขอบคุณ', 'khɔ̀ɔp khun', 'khop khun')]),
  lesson('numbers', 'Numbers and prices', ['Recognize useful numbers', 'Ask a price politely', 'Understand a price in baht'], [
    ('หนึ่ง', 'nʉ̀ng', 'One'), ('สอง', 'sɔ̌ɔng', 'Two'), ('สาม', 'sǎam', 'Three'), ('สิบ', 'sìp', 'Ten'),
    ('ยี่สิบ', 'yîi sìp', 'Twenty'), ('ร้อย', 'rɔ́ɔi', 'Hundred'), ('บาท', 'bàat', 'Baht'), ('เท่าไหร่', 'thâo rài', 'How much?')], [
    ('สวัสดีครับ เท่าไหร่ครับ', 'sà wàt dii khráp thâo rài khráp', 'Hello. How much is it?'),
    ('ยี่สิบบาทค่ะ', 'yîi sìp bàat khâ', 'Twenty baht.'),
    ('ขอบคุณครับ', 'khɔ̀ɔp khun khráp', 'Thank you.')],
    'Item + เท่าไหร่ + polite particle = How much is the item? Number + บาท = price in baht. สิบเอ็ด = 11; ยี่สิบเอ็ด = 21.',
    'You are at a market. Ask prices and buy two items. Reuse hello and thank you.', [
      mc('ยี่สิบบาท is how much?', ['20 baht', '2 baht', '100 baht'], '20 baht'),
      mc('Which means two?', ['หนึ่ง', 'สอง', 'สาม'], 'สอง'),
      blank('สิบ ___ (Ten baht)', 'บาท', 'bàat', 'baht'),
      blank('___ ครับ (How much?)', 'เท่าไหร่', 'thâo rài', 'thao rai')]),
  lesson('food', 'Ordering food and drinks', ['Order fried rice and water', 'Specify quantity with a classifier', 'Request non-spicy food'], [
    ('ขอ', 'khɔ̌ɔ', 'May I have / please give me'), ('ข้าว', 'khâao', 'Rice'), ('น้ำ', 'náam', 'Water'),
    ('กาแฟ', 'kaa fɛɛ', 'Coffee'), ('แก้ว', 'kɛ̂ɛo', 'Glass; classifier for drinks served by the glass'), ('จาน', 'jaan', 'Plate; classifier for food served by the plate'),
    ('ไม่เผ็ด', 'mâi phèt', 'Not spicy'), ('อร่อย', 'à rɔ̀i', 'Delicious')], [
    ('ขอข้าวผัดหนึ่งจาน ไม่เผ็ดครับ', 'khɔ̌ɔ khâao phàt nʉ̀ng jaan mâi phèt khráp', 'One plate of fried rice, not spicy, please.'),
    ('ขอน้ำหนึ่งแก้วครับ', 'khɔ̌ɔ náam nʉ̀ng kɛ̂ɛo khráp', 'One glass of water, please.'),
    ('ยี่สิบบาทค่ะ', 'yîi sìp bàat khâ', 'Twenty baht.'),
    ('อร่อยครับ ขอบคุณครับ', 'à rɔ̀i khráp khɔ̀ɔp khun khráp', 'Delicious. Thank you.')],
    'ขอ + item + number + classifier + ครับ / ค่ะ. ข้าวผัด (khâao phàt) = fried rice. ไม่เผ็ด means not spicy, not slightly spicy. แก้ว counts drinks served by the glass; จาน counts platefuls of food, not empty plates. Reuse หนึ่ง and บาท.',
    'Order fried rice and a drink at a café. Ask for non-spicy food, then ask the price.', [
      mc('What does ไม่เผ็ด mean?', ['Not spicy', 'Very spicy', 'Coffee'], 'Not spicy'),
      mc('Choose the classifier for a glass of water.', ['แก้ว', 'จาน', 'บาท'], 'แก้ว'),
      blank('___ น้ำหนึ่งแก้วครับ (May I have a glass of water?)', 'ขอ', 'khɔ̌ɔ', 'kho'),
      blank('ขอข้าวหนึ่ง ___ (One plate of rice, please)', 'จาน', 'jaan', 'jan')]),
  lesson('directions', 'Asking for directions', ['Ask where a place is', 'Understand left, right, and straight ahead', 'Confirm directions politely'], [
    ('อยู่ที่ไหน', 'yùu thîi nǎi', 'Where is …?'), ('ห้องน้ำ', 'hɔ̂ng náam', 'Toilet'), ('ไป', 'pai', 'Go'),
    ('ตรงไป', 'trong pai', 'Go straight'), ('เลี้ยวซ้าย', 'líao sáai', 'Turn left'), ('เลี้ยวขวา', 'líao khwǎa', 'Turn right'),
    ('ใกล้', 'klâi', 'Near'), ('ไกล', 'klai', 'Far')], [
    ('สวัสดีค่ะ ห้องน้ำอยู่ที่ไหนคะ', 'sà wàt dii khâ hɔ̂ng náam yùu thîi nǎi khá', 'Hello. Where is the toilet?'),
    ('ตรงไป แล้วเลี้ยวซ้ายครับ', 'trong pai lɛ́ɛo líao sáai khráp', 'Go straight, then turn left.'),
    ('ขอบคุณค่ะ', 'khɔ̀ɔp khun khâ', 'Thank you.')],
    'Place + อยู่ที่ไหน + ครับ / คะ = Where is the place? แล้ว = then. ใกล้ (falling) and ไกล (mid) differ in tone and meaning.',
    'Ask a local for the toilet and a café. Repeat the directions to check your understanding.', [
      mc('เลี้ยวขวา means …', ['Turn right', 'Turn left', 'Go straight'], 'Turn right'),
      mc('Which word means near?', ['ใกล้', 'ไกล', 'ไป'], 'ใกล้'),
      blank('ห้องน้ำ ___ คะ (Where is the toilet?)', 'อยู่ที่ไหน', 'yùu thîi nǎi', 'yu thi nai'),
      blank('___ แล้วเลี้ยวซ้าย (Go straight, then turn left)', 'ตรงไป', 'trong pai')]),
  lesson('shopping', 'Shopping and everyday conversations', ['Ask for an item and its price', 'Say what you want or decline politely', 'Combine greetings, numbers, and requests'], [
    ('เอา', 'ao', 'Take / want'), ('ไม่เอา', 'mâi ao', 'Do not want'), ('อันนี้', 'an níi', 'This one'),
    ('อันนั้น', 'an nán', 'That one'), ('มี', 'mii', 'Have / there is'), ('ไหม', 'mǎi', 'Yes/no question particle (often pronounced mái in conversation)'),
    ('ถุง', 'thǔng', 'Bag'), ('ได้', 'dâai', 'Can / okay')], [
    ('สวัสดีค่ะ อันนี้เท่าไหร่คะ', 'sà wàt dii khâ an níi thâo rài khá', 'Hello. How much is this one?'),
    ('สามสิบบาทครับ', 'sǎam sìp bàat khráp', 'Thirty baht.'),
    ('เอาอันนี้ค่ะ มีถุงไหมคะ', 'ao an níi khâ mii thǔng mǎi khá', 'I’ll take this one. Do you have a bag?'),
    ('มีครับ', 'mii khráp', 'Yes, we do.'),
    ('ขอบคุณค่ะ', 'khɔ̀ɔp khun khâ', 'Thank you.')],
    'มี + item + ไหม = Do you have …? เอา + item = I’ll take … . ไม่เอา + ครับ / ค่ะ = I do not want it (a direct refusal, softened by the particle). Add ขอบคุณ to thank the listener. อันนี้ is a generic this one; use the appropriate classifier when naming a specific kind of object. สามสิบ = 30.',
    'Buy something at a neighborhood shop. Ask the price, choose an item, request a bag, and say thank you.', [
      mc('How do you politely decline?', ['ไม่เอาค่ะ', 'เอาอันนี้ค่ะ', 'มีค่ะ'], 'ไม่เอาค่ะ'),
      mc('สามสิบบาท means …', ['30 baht', '3 baht', '13 baht'], '30 baht'),
      blank('มีถุง ___ คะ (Do you have a bag?)', 'ไหม', 'mǎi', 'mai', 'mái'),
      blank('เอา ___ ค่ะ (I’ll take this one)', 'อันนี้', 'an níi', 'an ni')])
]
TONES = [
  ('Mid', 'มา', 'maa', 'come', 'Keep your pitch level.'),
  ('Low', 'ข่า', 'khàa', 'galangal', 'Use a low pitch.'),
  ('Falling', 'ข้าว', 'khâao', 'rice', 'Start high and fall.'),
  ('High', 'ม้า', 'máa', 'horse', 'Use a high pitch.'),
  ('Rising', 'หมา', 'mǎa', 'dog', 'Start low and rise.')
]
