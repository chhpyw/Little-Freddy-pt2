"""Tone examples checked against NIU Spoken Thai, Unit 1, practices 1–5.

Contours are schematic teaching aids, not acoustic measurements.
Conversation phrases reuse the existing A1 curriculum.
"""
TONE_SOURCE = 'https://seasite.niu.edu/thai/spokenthai/unit1/practice/practice.htm'
TONE_GUIDE = [
  dict(id='mid', title='Mid', thai='ดี', roman='dii', english='Good',
       explanation='Keep your pitch around the middle of your comfortable range.', contour='20,55 65,55 110,55 155,55'),
  dict(id='low', title='Low', thai='สี่', roman='sìi', english='Four',
       explanation='Begin below the middle and let your pitch settle lower.', contour='20,65 65,80 110,85 155,85'),
  dict(id='falling', title='Falling', thai='ใช่', roman='châi', english='Yes / correct',
       explanation='Start relatively high, then drop toward the bottom of your range. ใช่ (châi) is valid for yes / correct in context. Polite forms: ใช่ค่ะ (châi khâ) / ใช่ครับ (châi khráp). Not every yes/no question is answered with ใช่.', contour='20,35 65,25 110,60 155,85'),
  dict(id='high', title='High', thai='ซ้าย', roman='sáai', english='Left',
       explanation='Start above the middle and move toward a higher pitch.', contour='20,50 65,45 110,25 155,20'),
  dict(id='rising', title='Rising', thai='ขวา', roman='khwǎa', english='Right',
       explanation='Begin low, dip slightly, then rise.', contour='20,70 65,85 110,60 155,25')
]
CONVERSATIONS = [
  dict(id='greeting', topic='Greetings', thai='สวัสดีครับ', roman='sà wàt dii khráp', english='Hello (polite)',
       options=['Hello (polite)', 'Thank you', 'Excuse me']),
  dict(id='introduction', topic='Introductions', thai='ผมชื่อเฟรดดี้ครับ', roman='phǒm chʉ̂ʉ Freddy khráp', english='My name is Freddy',
       options=['My name is Freddy', 'What is your name?', 'I am fine']),
  dict(id='food', topic='Food ordering', thai='ขอน้ำหนึ่งแก้วครับ', roman='khɔ̌ɔ náam nʉ̀ng kɛ̂ɛo khráp', english='One glass of water, please',
       options=['One glass of water, please', 'Two coffees, please', 'Not spicy, please']),
  dict(id='shopping', topic='Shopping', thai='อันนี้เท่าไหร่คะ', roman='an níi thâo rài khá', english='How much is this one?',
       options=['How much is this one?', 'I do not want a bag', 'I will take that one']),
  dict(id='directions', topic='Directions', thai='ห้องน้ำอยู่ที่ไหนคะ', roman='hɔ̂ng náam yùu thîi nǎi khá', english='Where is the toilet?',
       options=['Where is the toilet?', 'Turn right', 'Go straight']),
  dict(id='casual-introduction', topic='Casual introduction', thai='ชื่อแอนค่ะ', roman='chʉ̂ʉ ɛɛn khâ', english='My name is Ann (casual introduction)',
       options=['My name is Ann (casual introduction)', 'What is your name?', 'Thank you']),
  dict(id='nearby-restroom', topic='Nearby location', thai='ห้องน้ำอยู่แถวนี้ค่ะ', roman='hɔ̂ng náam yùu thɛ̌ɛo níi khâ', english='The restroom is around here',
       options=['The restroom is around here', 'The restroom is far from here', 'Turn right']),
  dict(id='far-restroom', topic='Far location', thai='ห้องน้ำอยู่ไกลจากที่นี่ค่ะ', roman='hɔ̂ng náam yùu klai jàak thîi nîi khâ', english='The restroom is far from here',
       options=['The restroom is far from here', 'The restroom is around here', 'Go straight']),
  dict(id='bag-decline', topic='Declining an offered bag', thai='ไม่รับถุงค่ะ ขอบคุณค่ะ', roman='mâi ráp thǔng khâ khɔ̀ɔp khun khâ', english='I won’t take a bag, thank you',
       options=['I won’t take a bag, thank you', 'Do you have a bag?', 'I will take that one']),
  dict(id='non-spicy-rice', topic='Ordering non-spicy fried rice', thai='ขอข้าวผัดหนึ่งจาน ไม่เผ็ดนะครับ', roman='khɔ̌ɔ khâao phàt nʉ̀ng jaan mâi phèt ná khráp', english='One plate of fried rice, not spicy, please',
       options=['One plate of fried rice, not spicy, please', 'One glass of water, please', 'Two coffees, please']),
  dict(id='bag-question', topic='Asking for a bag', thai='มีถุงไหมคะ', roman='mii thǔng mái khá', english='Do you have a bag?',
       options=['Do you have a bag?', 'I won’t take a bag, thank you', 'How much is this one?'])
]
SPEECH_ITEMS = [dict(id='tone-' + tone['id'], topic='Tone: ' + tone['title'],
                     thai=tone['thai'], roman=tone['roman'], english=tone['english'],
                     answer=tone['title'], options=[entry['title'] for entry in TONE_GUIDE])
                for tone in TONE_GUIDE] + [dict(item, answer=item['english']) for item in CONVERSATIONS]
