# Freddy Learns Thai language accuracy audit

Audit date: 14 November 2026, Asia/Bangkok.

## Usability recovery update on 16 November

A stale Flask process was serving old unstructured replies and qwen3:1.7b to the newer frontend. It has been restarted on port 5055 with qwen3.5:4b, confirmed by a real request and Ollama model metadata. Structured recovery now separates timeouts from validation failures, preserves drafts and offers explicitly labeled reviewed curriculum fallback in supported contexts. Rejected replies never enter history. Actual results: 88 Python tests passed, four JavaScript suites passed; six-turn real Flask HTTP restaurant dialogue passed 6/6 with accepted AI commentary and no fallback. SQLite checksum unchanged. See [diagnosis, results and limitations](tutor-usability-fix.md) and [recorded live dialogue](restaurant-flow-results.json). No native verification is claimed. No push was made.

## Latest reliability update on 15 November

qwen3.5:4b is now the configurable default; CHAT_MODEL overrides it. Supported fixed beginner examples, meanings, guides and usage notes come from reviewed curriculum IDs. Generated conversation is separately labeled unreviewed; no native verification is claimed. Wrong-script rejection and one clean-history retry remain active. RAG, source citations, lessons, vocabulary and SQLite data are preserved.

The [human-reviewable semantic benchmark](tutor-reliability-benchmark.md) records 12 cases covering greetings, food, directions, numbers, shopping and polite speech. Both models matched all 12 fixed goldens. Assistant editorial screening of generated commentary found clear errors in 5/12 responses for qwen3:1.7b and 2/12 for qwen3.5:4b, with one additional register concern for the smaller model. This is not a native or comprehensive language-accuracy grade. Repeated script/schema results were 9 accepted / 3 rejected for each model. Final live PDF/RAG checks were 8 passed / 2 failed for 1.7b and 10 passed / 0 failed for 4b. Automated results: 82 Python tests passed, 0 failed; all four JavaScript suites passed. Personal storage checksums remained unchanged. No push was made.

Earlier sections below retain their original acceptance policies and historical model defaults; the linked reliability report describes the current implementation and failed cases.

## Tutor script safety follow-up

The most recent change replaces the earlier warning-only behavior with structured tutor fields, server-side script validation, one clean-history retry and an error after failed generation. Invalid Burmese/Myanmar, Khmer and other-script teaching examples are not rendered or saved as tutor history. Legitimate other-language quotations and document titles remain possible in separate labeled fields. Old unvalidated assistant turns are filtered; learner messages and SQLite progress are preserved.

See [the full script-safety report](tutor-script-safety.md) for the Unicode ranges, API/frontend contract, hardware check, exact live outputs and reproduction commands. Final automated results are **77 Python tests passed, 0 failed; all 4 JavaScript suites passed**. Repeated live script/schema acceptance was **5 of 12** for qwen3:1.7b and **9 of 12** for the installed qwen3.5:4b. Invalid generations were blocked. PDF/RAG smoke results were **8 passed / 2 failed** for the default model and **10 passed / 0 failed** for the alternative. Neither these acceptance counts nor Unicode validation establish accurate Thai, English meanings, romanization or trustworthy model-supplied reference titles. Accepted outputs from both models still contained teaching errors.

The Apple M4 Pro / 24 GiB machine successfully ran the installed 4b model at a bounded 4096-token context. It is a compatible candidate for further evaluation, not a verified Thai teacher; no model was downloaded or default switched. The authored corrections below remain intact. No personal data was changed and nothing was committed or pushed in this follow-up. Earlier results below are historical and use the acceptance policy described for their own step.

## Earlier context review applied

The user's Thai-language review is applied below. This records the supplied review, not independent native verification. This section and [the current human-review table](thai-human-review.md) supersede earlier phrase decisions in the historical audit tables.

| Context | Current Thai | Romanization | English and teaching decision |
| --- | --- | --- | --- |
| Nearby restroom | ห้องน้ำอยู่แถวนี้ค่ะ | hɔ̂ng náam yùu thɛ̌ɛo níi khâ | The restroom is around here. Added to the near-context card, an alternative directions reply and a new speech item. แถวนี้ is labeled as a contextual near expression, not a literal reading of ใกล้. |
| Far restroom | ห้องน้ำอยู่ไกลจากที่นี่ค่ะ | hɔ̂ng náam yùu klai jàak thîi nîi khâ | The restroom is far from here. Reference point is explicit across card, dialogue and speech. |
| Declining an offered bag | ไม่รับถุงค่ะ ขอบคุณค่ะ | mâi ráp thǔng khâ khɔ̀ɔp khun khâ | I won’t take a bag, thank you. Added to the ถุง card, alternative shop reply, contextual quiz and new speech item. ไม่เอา retains a separately labeled direct general refusal containing that headword. |
| Non-spicy fried rice | ขอข้าวผัดหนึ่งจาน ไม่เผ็ดนะครับ | khɔ̌ɔ khâao phàt nʉ̀ng jaan mâi phèt ná khráp | One plate of fried rice, not spicy, please. The softening นะครับ is reflected in the dialogue, derived cards and new speech exercise. |
| Casual introduction | ชื่อแอนค่ะ | chʉ̂ʉ ɛɛn khâ | My name is Ann. Pronoun omission is explained in the pattern, dialogue, ชื่อ card and new speech item. |
| Valid introduction alternative | ฉันชื่อแอนค่ะ | chǎn chʉ̂ʉ ɛɛn khâ | My name is Ann, with an explicit familiar pronoun. Retained on the ฉัน card and in the dialogue as a valid alternative. |
| Confirmation | ใช่; ใช่ค่ะ / ใช่ครับ | châi; châi khâ / châi khráp | Yes / correct in context. The tone target remains ใช่; the guide explains polite forms and question-dependent answers. |
| Bag question | มีถุงไหมคะ | mii thǔng mái khá | Do you have a bag? Correct Thai retained; the new speech item uses conversational high mái. |

ใกล้ remains falling klâi and ไกล remains mid klai. คะ is high khá for the feminine polite question; ค่ะ is falling khâ for the statement. ไหม retains rising citation-form mǎi in its vocabulary/quiz guide; conversational high mái appears in the shopping dialogue and bag-question exercise. Both remain accepted romanized quiz answers, along with the historical unmarked alias. Citation form here means the isolated/classroom pronunciation, not a reference to document citations.

Correct coffee and coconut-water expressions are preserved: ขอกาแฟหนึ่งแก้วค่ะ and ขอน้ำมะพร้าวหนึ่งแก้วครับ. The latter remains the documented correction for earlier chatbot output; it was not replaced or expanded with invented ingredients. Application chat/RAG logic and source-citation rendering are unchanged.

Directions and shopping label the new replies as alternative situations, not contradictory turns in one transaction. Current totals are 23 dialogue lines, 40 vocabulary headwords, 20 quiz questions and 16 example overrides. Six additional speech items bring the catalog to 16 items / 32 activity states. Existing speech IDs/target texts and lesson IDs remain intact. Saved completions remain; the displayed speech denominator grows with new activities. The bag-refusal quiz now asks specifically about declining an offered bag and thanking the seller; saved lesson scores are not recalculated.

Twelve exact pre-review built-in snapshots were added to the updater's manifest, bringing it to 35 historical snapshots. Tests check every version independently, including multiple versions sharing one Thai key. Manual/edited cards and scheduling/review fields remain protected. A current-database preview found zero saved cards to update; no content migration was applied to personal storage. The progress.sqlite3 checksum remains unchanged from the preceding follow-up.

Final context-review validation: **70 Python tests passed, 0 failed; all 4 JavaScript suites passed; all 4 application scripts parsed; git diff --check passed.** This includes language, RAG/citation, persistence and safe-updater regressions. The near-card regression explicitly checks the reviewed แถวนี้ phrase and its contextual label instead of assuming every example literally contains its headword. No new live-model or device-audio evaluation was performed in this step. Names, TTS tones, prosody, pronoun pronunciation and relationship-dependent register remain human-review items. No commit or push was made.

The authored beginner material is largely understandable, but the food dialogue has a context mismatch and several explanations oversimplify register or classifiers. Pronunciation notation is inconsistent between lessons, quizzes and decorative text. The corrections below address these issues. They do not establish the accuracy of arbitrary model-generated replies. **No native-speaker verification was performed.**

## Scope and evidence

The initial audit reviewed all five A1 lessons: 40 vocabulary entries, 18 dialogue lines, 20 quiz questions including distractors and accepted answers, five sentence patterns, objectives and scenarios. Also reviewed the four course roadmaps, five curriculum tone examples, five speaking/listening tone examples and their pitch hints, five conversation activities, all 14 then-existing vocabulary-example overrides and the 40 resulting catalog cards, Thai interface text, pronunciation guidance, all tutor levels/modes, lesson context and retry prompts. The historical inventory below preserves the initial original/result pairs; the latest context review above records subsequent changes.

Uploaded documents, saved personal words, learner records and historical model outputs are not curated course content. The initial audit did not edit personal storage or generate a new live chat sample. The subsequent follow-up below records a fresh live check and a conservative saved-card update tool.

References are teaching resources, not a substitute for review by a qualified Thai teacher. Their transcription systems differ; the app uses the convention defined below. Some older NIU pages also contain inconsistent accents or particle spellings, so individual printed forms were not copied indiscriminately.

| Reference | What it supports |
| --- | --- |
| [NIU Spoken Thai Unit 1 basic phrases](https://seasite.niu.edu/thai/spokenthai/unit1/basic/wordmain.htm) | Greetings, self-reference, polite speech, questions and directions. |
| [NIU Unit 1 vocabulary](https://seasite.niu.edu/thai/spokenthai/unit1/finder/default.htm) | Vowel distinctions/length, numbers, coffee, question words, then/already. |
| [NIU Unit 1 tone practice](https://seasite.niu.edu/thai/spokenthai/unit1/practice/practice.htm) | Tone examples and the rising written/high conversational pronunciation of ไหม. |
| [NIU teaching plan](https://seasite.niu.edu/thai/FLTH/teaching_plan.htm) | Name questions, masculine/feminine polite forms and asking locations. |
| [Sandee Thai Language School beginner textbook](https://www.sandee.ac.th/wp-content/uploads/2023/08/Sandee-Level-1-Book.pdf) | Beginner vocabulary, particles and classifier instruction. Different romanization is not itself a Thai error. |
| [Palm Samran consonant lesson](https://palmsamran.com/free-thai-lessons/read-thai-script/middle-class-consonant/) | ก letter name, unaspirated initials and short/long vowels. |
| [Tuttle Reading and Writing Thai vocabulary cards](https://www.tuttlepublishing.com/content/docs/9780804853798/Flash%20Cards/Set%202_%20Vocabulary%20Cards%201%20to%2050.pdf) | Name/self-introduction patterns and familiar ฉัน. |
| [Thai With Grace greeting lesson](https://thaiwithgrace.com/hello-in-thai/) | สวัสดี can be used on meeting or parting, so a goodbye distractor is ambiguous without context. |

The non-spicy fried-rice replacement and register explanations are editorial judgments based on meaning and the request/classifier patterns, not quotations or native sign-off. The A2 roadmap clarification distinguishes completion/change of state from a general English past tense; NIU lists both temporal sequencing and already senses for แล้ว.

## Corrections and explanations

“Applied” means the authored source changed. “Retained” means no clear error was identified; it does not mean every usage has native approval. Pronunciation standardization does not imply that every alternate transcription is wrong.

| Location | Original text | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| Food dialogue and derived cards | ขอข้าวหนึ่งจานครับ ไม่เผ็ดครับ / One plate of rice, please. Not spicy, please. | Plain rice is an unsuitable example for a non-spicy preparation request. Grammar alone is understandable. | **Applied:** ขอข้าวผัดหนึ่งจาน ไม่เผ็ดครับ / One plate of fried rice, not spicy, please. | Gives the request an actual prepared-dish context. ข้าว still means rice; ผัด contributes fried/stir-fried. Added khâao phàt and the compound meaning to the pattern. Scenario/objectives now agree. A teacher should still assess restaurant naturalness and the invented price context. |
| Food objective | Request mild food | Mild can mean slightly spicy; ไม่เผ็ด means not spicy. | **Applied:** Request non-spicy food. | Does not teach “a little spicy” as equivalent to “not spicy.” |
| Greetings and repeated speech material | สวัสดี / sawàt dii | The first syllable has no low-tone marking although the displayed legend says unmarked vowels have mid tone. | **Applied:** sà wàt dii in vocabulary, dialogues and speech activities. | Shows the full teaching pronunciation and syllables. Reduced initial syllables in natural speech remain possible. NIU gives a low initial syllable in its basic greeting. |
| Greeting question | อะไร / àrai | Syllables run together while other multi-syllable examples are separated. | **Applied:** à rai. | Segmentation change only; the first syllable is low and rai is mid in this notation. |
| Food vocabulary and examples | กาแฟ / gaa fae | Uses g for ก while ใกล้ uses k; ae does not state vowel length under the existing legend. | **Applied:** kaa fɛɛ throughout authored content. | Initial k is unaspirated; both vowels are long. NIU distinguishes the open-front vowel in its own notation. |
| Food and speech examples | แก้ว / kâew | The ae spelling does not state the vowel quality/length consistently with the other special vowel symbols. | **Applied:** kɛ̂ɛo. | Falling tone, long open-front vowel plus final glide. This is a chosen pronunciation convention; gâew and similar systems are not inherently wrong. |
| Directions dialogue | แล้ว / láew | Same inconsistent ae notation. | **Applied:** lɛ́ɛo. | High tone, long open-front vowel plus glide; the dialogue correctly uses the sequencing sense “then.” |
| Food vocabulary/dialogue | อร่อย / àrɔ̀i | Syllable separation inconsistent. | **Applied:** à rɔ̀i. | Both syllables remain low; translation “delicious” is retained. |
| Blank quiz hints | chue; khop khun; baht; thao rai; kho; jan; yu thi nai; mai; an ni | Hints omit tones, vowel distinctions and/or length, contradicting vocabulary and the pronunciation legend. | **Applied:** chʉ̂ʉ; khɔ̀ɔp khun; bàat; thâo rài; khɔ̌ɔ; jaan; yùu thîi nǎi; mǎi; an níi. | Displayed hints now match their vocabulary entries. All old strings remain accepted input aliases; mái is also accepted for the conversational question particle. trong pai already matched and remains unchanged. |
| Greeting listening options | สวัสดีครับ; Hello (polite) / Thank you / Goodbye for now | The phrase can also be used on parting, so the goodbye distractor is not unambiguously wrong. | **Applied:** replace Goodbye for now with Excuse me; retain the greeting answer and target text. | Avoid penalizing a legitimate contextual meaning when the clip gives no meeting/parting context. Teacher Grace's lesson explicitly describes both uses. Historical attempt scores are not rewritten. |
| Vocabulary example | ฉันชื่อแอนค่ะ / chǎn chʉ̂ʉ Ann khâ | English spelling is not a pronunciation guide for แอน. | **Applied:** chǎn chʉ̂ʉ ɛɛn khâ; English “My name is Ann” retained. | The Thai spelling here has a long open-front vowel. The intended person's own preferred name pronunciation still needs confirmation. |
| Pronoun glossary | ฉัน / I; ผม / I, commonly used by men; คุณ / You | Meanings lack register guidance. | **Applied:** familiar/often feminine note for ฉัน, polite masculine use for ผม, polite/neutral for คุณ; pattern mentions formal feminine ดิฉัน. | Pronouns depend on relationship and style, not a universal English-I/you substitution. Do not force gender identity from particles. Familiar ฉัน is not automatically wrong. |
| Food classifier glosses | แก้ว / Glass / cup classifier; จาน / Plate classifier | Could imply every cup uses แก้ว or empty plates are counted with จาน. | **Applied:** drinks served by the glass; food served by the plate; pattern distinguishes platefuls from empty plates. | Classifier follows the referent/serving. Existing หนึ่งแก้ว water and หนึ่งจาน rice structures are correct. Hot coffee in a cup may use ถ้วย; do not rewrite a legitimate glass serving as an error. |
| Food pattern | ไม่ + adjective negates it. | Too broad as a complete beginner grammar rule. | **Applied:** explain ไม่เผ็ด directly and its non-spicy meaning. | Keeps instruction tied to the example rather than claiming a complete account of Thai negation. |
| Shopping particle | ไหม / mǎi / Yes/no question particle | Missing common spoken high-tone variant. | **Applied:** note conversational mái; retain written-form mǎi and accept both in quiz. | NIU explicitly distinguishes these readings. Not a blanket replacement of the spelling ไหม or of every rising tone. |
| Shopping pattern | ไม่เอา + ครับ / ค่ะ = No, thank you. | Pragmatic English gloss hides a direct “do not want” and may sound blunt in some settings. | **Applied:** explain direct refusal, particle softening and adding ขอบคุณ for thanks. | The original answer is a valid polite-particle refusal, so the quiz answer is retained; a native teacher should assess the best default refusal style. |
| Shopping pattern | เอา + item; อันนี้ vocabulary | A learner may generalize generic อัน to every named object. | **Applied:** explain generic “this one” versus using a specific object's classifier. | The actual dialogue is acceptable with a visible, unspecified item. |
| A2 roadmap | Describe past experiences with แล้ว | Risks equating แล้ว with a general past/experiential marker. | **Applied:** completed actions and changed situations; not a general past-tense marker. | A roadmap clarification, not a new scored course. Experience may require เคย and additional context; no claim that แล้ว alone expresses all past experience. |
| Decorative alphabet label | ก ไก่ · gor gai | Uses a third notation and gives no low tone for ไก่; English r may be pronounced incorrectly. | **Applied:** ก ไก่ · kɔɔ kài. | Letter name followed by mnemonic noun; k is unaspirated, ɔɔ long, kài low. The Thai ก ไก่ itself was correct. Layout/classes are retained. |
| Tutor welcome and reset message | Sawasdee! สวัสดี!; Sawasdee! What would you like to practice today? | Informal English spelling conflicts with the teaching convention. | **Applied:** สวัสดี! (sà wàt dii — Hello!) in both messages. | Same greeting, consistent pronunciation and explicit English meaning. The dashboard's English heading “Sawasdee, Freddy” is retained as a salutation, not a phonetic guide. |
| Pronunciation legend | Tone marks only; no explanation of vowel doubling, ɔ/ɛ/ʉ or aspiration | Learners cannot consistently interpret the guide. | **Applied:** add those distinctions, glide notation, j/ch convention and proper-name exception. | An app-specific reading aid, not IPA or RTGS. No promise that TTS supplies a precise tone model. |
| Tutor prompts across levels/modes | Relevant Thai, English explanations and general teaching instructions; no explicit meaning/classifier check or consistent pronunciation convention | Thai script presence does not ensure accurate Thai or a matching English translation. | **Applied:** ask for matching meaning, natural structure, appropriate classifier/serving, particle style and consistent pronunciation; acknowledge uncertainty and never claim native verification. | Prompt guidance can reduce errors but cannot verify output. Retained every level/mode, translation preference, reference context, source instructions, bounded retry and generation settings. |

## Material retained and items requiring teacher review

| Original text or behavior | Issue or review question | Proposed correction or decision | Explanation |
| --- | --- | --- | --- |
| เฟรดดี้ / Freddy | Romanization column retains an English proper name rather than transcribing the Thai loanword. Exact intended pronunciation is unknown. | **Native-speaker/name-owner review:** retain spelling and Freddy until an approved spoken form is established. Legend now identifies this exception. | Do not invent tone-marked Thai-name pronunciation from the English spelling. Speech text and item IDs remain stable. |
| ฉัน / chǎn | Familiar self-reference often has conversational chán; relationships and speaker style matter. | **Teacher review:** retain written-form chǎn and register note; decide whether a separately labeled conversational variant belongs in A1. | Not all differing pronunciations indicate a translation error. |
| ห้องน้ำอยู่ใกล้ค่ะ / The toilet is nearby | The reference point is implicit. | **Teacher review:** retain the elliptical phrase; for a stand-alone card consider ห้องน้ำอยู่ใกล้ที่นี่ค่ะ / The toilet is near here. | Original is not demonstrably ungrammatical. A more explicit reference point could improve context. |
| ห้องน้ำอยู่ไกลค่ะ / The toilet is far away | Reference point similarly implicit. | **Teacher review:** retain; consider explicitly “far from here” if that is the intended scenario. | Do not add a reference point and silently pretend it was in the original. |
| ไม่เอาค่ะ; เอาอันนี้ค่ะ | Direct transactional style may be brusque depending on relationship and intonation. | **Teacher review:** retain accurate literal meaning and new register note; assess adding a gentler refusal such as ไม่เป็นไรค่ะ ขอบคุณค่ะ in a future lesson. | A polite particle is not a guarantee of a universally suitable tone. |
| สวัสดีครับ ผมชื่อเฟรดดี้ | Final statement has no second ครับ. | **Retained.** Optional final ครับ is a style refinement, not a required grammatical repair. | Initial greeting is already polite. |
| เท่าไหร่; อันนี้เท่าไหร่คะ | Colloquial price question, item implicit or visible. | **Retained.** ราคาเท่าไหร่ may be taught as an expanded variant. | Do not “correct” a natural short price question into a mandatory formal form. |
| ขอน้ำหนึ่งแก้วครับ; ขอกาแฟหนึ่งแก้วค่ะ | Serving/container dependency. | **Retained.** Water and coffee served by the glass are legitimate. | Review TTS and the intended café setting with a teacher; not every hot cup should be taught with the same classifier. |
| ใกล้ / klâi; ไกล / klai | Falling versus mid contrast. | **Retained.** | The lexical meanings and marked contrast are correct; real speech also varies in duration. |
| มา/maa, ข่า/khàa, ข้าว/khâao, ม้า/máa, หมา/mǎa | Curriculum tone examples. | **Retained.** | Meanings and five tone assignments agree with standard readings. Pitch hints are schematic; require teacher/audio review before treating playback as a model. |
| ดี/dii, สี่/sìi, ใช่/châi, ซ้าย/sáai, ขวา/khwǎa | Speaking/listening tone examples. | **Retained.** | Mid, low, falling, high, rising assignments are appropriate. ใช่ is “yes/correct” in relevant contexts, not a universal yes answer to every Thai question. |
| Rising/high/falling pitch diagrams and hints | A single drawn contour cannot capture duration, sentence position, speaker range or all contextual variation. | **Teacher/device review:** retain illustrative labeling; listen to each installed Thai TTS voice and compare against teacher-approved recordings. | No waveform analysis or pronunciation assessment is implemented. The app must not claim otherwise. |
| ทีละนิด ทุกวัน; เรียนรู้ไปด้วยกัน | Sidebar slogan and footer. | **Retained.** | “A little at a time, every day” and “learn together” fit the intended UI. “A little Thai” is contextual adaptation; Thai is not literally in the slogan. ฟ is a decorative brand initial, not a vocabulary translation. |
| A1/A2/B1/B2 labels | Curriculum alignment and real proficiency level not externally assessed. | **Teacher review:** retain existing roadmap distinction; commission pedagogical/CEFR alignment separately. | Language editing does not certify course level or learning outcomes. |

## Previously observed chatbot errors

These examples are from the prior integration replies, not authored lesson strings or a new audit-time live run. Proposed replacements are editorial suggestions needing teacher review for final release; the application must not insert them mechanically after unrelated replies.

| Original response excerpt | Issue | Proposed correction | Explanation |
| --- | --- | --- | --- |
| Thai greeting: နှစ်သက္ကဋ္ဌ … | Burmese script offered as Thai; retry still failed. | สวัสดีครับ / Hello (masculine polite style), or สวัสดีค่ะ in the feminine polite style. | Match the requested language and the learner's preferred style. The existing missing-Thai warning is necessary but only detects omission. |
| ขอซีดีน้ำนมมะพร้าวแบบน้ำตาลทราย / I want to order coconut water with sugar. | Includes ซีดี (CD), shifts toward coconut milk, invents sugar and mismatches the requested coconut water. | ขอน้ำมะพร้าวหนึ่งแก้วครับ / One glass of coconut water, please. Feminine option: ค่ะ. | Restore the requested drink, quantity and serving without invented ingredients. |
| สวัสดีครับ/แม่! | แม่ means mother, not an alternate polite greeting particle. | สวัสดีครับ or สวัสดีค่ะ, with the style labeled. | Slash alternatives must represent actual alternatives for the intended construction. |
| ขอให้เป็นน้ำมะพร้าวแบบนี้เลย; ขอให้น้ำมะพร้าวแบบนี้ | Awkward item-ordering construction, changed “this type” meaning and an overconfident English explanation. | ขอน้ำมะพร้าวหนึ่งแก้วครับ / One glass of coconut water, please. | ขอให้ has valid uses such as wishes; it is not a literal replacement for every English “please.” The prompt now distinguishes item ordering. |
| Any reply passing the current Thai-character check | May still contain wrong words, tone guides or citations. | **Unresolved:** semantic/linguistic review of outputs and evaluation by a qualified Thai teacher. | Presence checks and prompt instructions cannot certify factual or language quality. No test was weakened to hide this limitation. |

## Pronunciation convention

The authored guide uses unmarked mid, grave low, circumflex falling, acute high and caron rising tones. Vowel doubling marks length (aa, ii, uu, ɔɔ, ɛɛ, ʉʉ). Initial k/p/t are unaspirated, kh/ph/th aspirated; j represents จ and ch represents ช/ฉ. The ɔ, ɛ and ʉ symbols identify distinct vowels. ai/ao are glides; aao and ɛɛo show a long vowel before the final glide. Compound and phrase syllables are separated where useful. This simplified aid omits some phonetic detail and is not IPA. The only retained English-name placeholder in pronunciation columns is Freddy, explicitly flagged above.

Quiz input remains lenient for historical unmarked aliases; these aliases are not displayed as the recommended pronunciation. Written mǎi and conversational mái are distinguished. A consistent notation does not make a synthetic voice or a chatbot's newly generated guide correct.

## Compatibility and validation

Lesson IDs, question order/Thai answer keys, vocabulary word order/Thai keys, speech item IDs/target Thai text and database schemas are unchanged. The ambiguous greeting distractor changed; historical scores are retained. Existing saved vocabulary is a snapshot; re-import does not overwrite duplicates. The follow-up adds an explicit maintenance tool for exact matches to known historical built-in snapshots. Manual/edited cards and unknown versions are left untouched, as are scheduling fields and review rows.

The initial language audit changed no RAG retrieval, citation rendering, storage, progress, review scheduling, request retry or generation-setting logic. The follow-up improves the standalone re-index utility and adds an explicit saved-card maintenance tool; application chat/retrieval logic and design remain unchanged. The earlier integration fix in app.py and tests/test_app.py was retained.

| Validation | Actual outcome |
| --- | --- |
| Python full suite | Latest context review: 70 passed, 0 failed (previous follow-up: 68 passes) with `.venv/bin/python -m unittest discover -s tests -q`. Initial language audit had 63 passes. Includes language regressions, two additional re-index tests and three saved-card update tests. |
| JavaScript suites | All 4 passed: navigation, tutor UI/citations, speech adapters, vocabulary UI. Used the provided Node runtime because standalone node is absent from shell PATH. |
| JavaScript syntax | All 4 application scripts parsed, including edited learning.js. |
| RAG and progress regressions | Existing mocked/integration extraction, retrieval/citations, rollback, persistence and concurrency tests passed as part of the Python/JavaScript suites. |
| Live Ollama and RAG | Previous follow-up, before the latest context review: 10 checks passed, 0 failed. Intermediate / Free Chat returned สวัสดีครับ followed by Hello!, HTTP 200, no warnings. Both retrieval answers contained 37 and the filename, with matching source metadata. This is a smoke test, not language-quality certification. |
| Manual acceptance | Native-speaker review, audible Thai TTS, real recognition and responsive visual inspection remain outstanding. |

Expected malformed-file/storage-error fixture logs are not test failures. No commit or GitHub push was made during this follow-up.

## Follow-up diagnosis and maintenance results

### Re-indexing investigation

The earlier `Processing thai.txt... FAILED (Incomplete embeddings; previous index kept)` line was emitted by `test_reindex_keeps_previous_chunks_on_partial_failure` in tests/test_integration.py. It creates a temporary 700-character file, mocks the first embedding as valid and the second as None, and expects zero successful documents with the previous index retained. It is a deliberate failure fixture, not evidence of a broken personal document or a failed live Ollama request. The current default uploads folder is empty and vector_index.json is absent; no real thai.txt could be repaired, and no personal index was rebuilt or deleted.

The utility nevertheless needed better diagnostics and transient-failure handling. It now retries a missing/invalid embedding up to twice per chunk by default (configurable from one to three attempts), identifies the failed chunk and reason, rejects inconsistent dimensions within a document, and publishes only complete document results. Unrelated vector entries survive successful re-indexing; exhausted retries and dimension failures leave the existing index byte-for-byte unchanged in regression tests. The CLI returns a nonzero exit code for document failures and can save a JSON report. It still requires Flask and other writers to be stopped; the JSON index is not a multi-process database. Service-specific causes must be checked in Ollama logs; the old fixture contains no such cause.

The new live synthetic thai.txt check succeeded: two chunks, both 768-dimensional embeddings, original file bytes retained during re-indexing. A synthetic PDF also re-indexed successfully. Both temporary documents were removed only from the isolated test directory after the checks.

### Saved vocabulary investigation

The configured default progress.sqlite3 contains zero saved vocabulary rows, so there were no outdated saved translations to update. No storage environment overrides were present. Preview and apply both reported total 0, eligible 0, updated 0; no backup was needed and the database SHA256 remained `972f1463afaca9f395bd49f5ac5232c92e16878bfe50b8a054b8bb0d31d9e68c` before and after the work.

For populated installations, src/vocabulary_legacy.json initially recorded 23 changed built-in snapshots from commit b9cb57c; the latest context review adds 12 prior-version snapshots, for 35 total. This includes pronunciation, register glosses and example translations, not 23 necessarily incorrect Thai headwords. The updater requires a nonempty lesson_id and an exact match of every stored content field to one of those snapshots before substituting the current catalog entry. A matching Thai headword alone never authorizes an overwrite. Manual cards, customized built-in cards, already current cards and unrecognized versions are preserved. A byte-identical recreation of a historical built-in card with the same lesson provenance cannot be distinguished from that historical import; arbitrary historical user edits are not inferred.

The apply operation locks writers, makes a complete SQLite backup beside the database with a unique `-before-content-….sqlite3` filename, and updates only the content fields in one transaction. IDs, Thai keys, creation dates, due dates, intervals, ease, repetitions, review revisions and review history do not change. A failing update rolls back all card changes and retains the backup. Tests cover all 35 historical snapshots independently, manual and edited cards, backups, historical review rows, unchanged scheduling, idempotency and a simulated mid-update storage failure. No automatic background migration was introduced.

Stop Flask during maintenance. Preview first; apply only after inspecting the eligible count:

```sh
.venv/bin/python scripts/update_builtin_vocabulary.py
.venv/bin/python scripts/update_builtin_vocabulary.py --apply
# For another installation, pass --database /absolute/path/to/progress.sqlite3.
# Re-index only when there are actual documents to process:
.venv/bin/python reindex.py --attempts 2 --report /tmp/freddy-reindex.json
```

### Human review and live evidence

The [concise human review table](thai-human-review.md) includes English meaning, Thai, romanization, context and the issue for 12 uncertain or context-sensitive phrases. It covers names, pronouns, refusals, implicit location references, dish/serving choices, question-particle pronunciation and prior chatbot corrections. **No native verification is claimed.**

Raw final results are in [followup-live-results.json](followup-live-results.json). Reproduce the targeted tutor, multi-chunk Thai text and PDF/RAG checks with:

```sh
.venv/bin/python scripts/live_ollama_smoke.py --tutor-level Intermediate --report /tmp/freddy-followup-live.json
```

The run used real local qwen3:1.7b and nomic-embed-text with temporary documents, index and learner database. The first sandboxed attempt could not reach the local service; the completed run outside that restriction passed all 10 checks. Both explicit and semantic RAG answers had the expected price and filename citation. The test now requires citations in the answer rather than merely recording their absence. The Intermediate reply was a relevant Thai greeting with an appropriate English meaning, but omitted romanization despite the pronunciation setting being enabled; the presence smoke test does not assert that preference or full teaching quality. Broader naturalness, pronunciation accuracy, all-mode reliability and device audio remain human acceptance work.

## Historical authored content inventory

The following original/result pairs make unchanged entries visible as well as corrections. Retained entries have no clear error identified in this audit; context and teacher-review qualifications above still apply. English distractors are intentionally incorrect answers, not proposed translations.

### Lesson vocabulary

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| greetings word 1 | สวัสดี / sawàt dii / Hello | Notation or contextual guidance | สวัสดี / sà wàt dii / Hello | Applied as explained in the corrections table. |
| greetings word 2 | ขอบคุณ / khɔ̀ɔp khun / Thank you | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| greetings word 3 | ครับ / khráp / Polite particle, commonly used by men | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| greetings word 4 | ค่ะ / khâ / Polite statement particle, commonly used by women | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| greetings word 5 | ชื่อ / chʉ̂ʉ / Name / be named | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| greetings word 6 | คุณ / khun / You | Notation or contextual guidance | คุณ / khun / You (polite / neutral) | Applied as explained in the corrections table. |
| greetings word 7 | ผม / phǒm / I, commonly used by men | Notation or contextual guidance | ผม / phǒm / I, commonly used by men in polite speech | Applied as explained in the corrections table. |
| greetings word 8 | ฉัน / chǎn / I | Notation or contextual guidance | ฉัน / chǎn / I (familiar; often used by women) | Applied as explained in the corrections table. |
| numbers word 1 | หนึ่ง / nʉ̀ng / One | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 2 | สอง / sɔ̌ɔng / Two | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 3 | สาม / sǎam / Three | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 4 | สิบ / sìp / Ten | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 5 | ยี่สิบ / yîi sìp / Twenty | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 6 | ร้อย / rɔ́ɔi / Hundred | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 7 | บาท / bàat / Baht | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers word 8 | เท่าไหร่ / thâo rài / How much? | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food word 1 | ขอ / khɔ̌ɔ / May I have / please give me | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food word 2 | ข้าว / khâao / Rice | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food word 3 | น้ำ / náam / Water | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food word 4 | กาแฟ / gaa fae / Coffee | Notation or contextual guidance | กาแฟ / kaa fɛɛ / Coffee | Applied as explained in the corrections table. |
| food word 5 | แก้ว / kâew / Glass / cup classifier | Notation or contextual guidance | แก้ว / kɛ̂ɛo / Glass; classifier for drinks served by the glass | Applied as explained in the corrections table. |
| food word 6 | จาน / jaan / Plate classifier | Notation or contextual guidance | จาน / jaan / Plate; classifier for food served by the plate | Applied as explained in the corrections table. |
| food word 7 | ไม่เผ็ด / mâi phèt / Not spicy | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food word 8 | อร่อย / àrɔ̀i / Delicious | Notation or contextual guidance | อร่อย / à rɔ̀i / Delicious | Applied as explained in the corrections table. |
| directions word 1 | อยู่ที่ไหน / yùu thîi nǎi / Where is …? | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 2 | ห้องน้ำ / hɔ̂ng náam / Toilet | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 3 | ไป / pai / Go | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 4 | ตรงไป / trong pai / Go straight | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 5 | เลี้ยวซ้าย / líao sáai / Turn left | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 6 | เลี้ยวขวา / líao khwǎa / Turn right | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 7 | ใกล้ / klâi / Near | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions word 8 | ไกล / klai / Far | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 1 | เอา / ao / Take / want | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 2 | ไม่เอา / mâi ao / Do not want | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 3 | อันนี้ / an níi / This one | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 4 | อันนั้น / an nán / That one | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 5 | มี / mii / Have / there is | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 6 | ไหม / mǎi / Yes/no question particle | Notation or contextual guidance | ไหม / mǎi / Yes/no question particle (often pronounced mái in conversation) | Applied as explained in the corrections table. |
| shopping word 7 | ถุง / thǔng / Bag | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping word 8 | ได้ / dâai / Can / okay | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |

### Lesson dialogues

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| greetings line 1 | สวัสดีครับ ผมชื่อเฟรดดี้ / sawàt dii khráp phǒm chʉ̂ʉ Freddy / Hello. My name is Freddy. | Notation or contextual guidance | สวัสดีครับ ผมชื่อเฟรดดี้ / sà wàt dii khráp phǒm chʉ̂ʉ Freddy / Hello. My name is Freddy. | Applied as explained in the corrections table. |
| greetings line 2 | สวัสดีค่ะ คุณชื่ออะไรคะ / sawàt dii khâ khun chʉ̂ʉ àrai khá / Hello. What is your name? | Notation or contextual guidance | สวัสดีค่ะ คุณชื่ออะไรคะ / sà wàt dii khâ khun chʉ̂ʉ à rai khá / Hello. What is your name? | Applied as explained in the corrections table. |
| greetings line 3 | ผมชื่อเฟรดดี้ครับ / phǒm chʉ̂ʉ Freddy khráp / My name is Freddy. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers line 1 | สวัสดีครับ เท่าไหร่ครับ / sawàt dii khráp thâo rài khráp / Hello. How much is it? | Notation or contextual guidance | สวัสดีครับ เท่าไหร่ครับ / sà wàt dii khráp thâo rài khráp / Hello. How much is it? | Applied as explained in the corrections table. |
| numbers line 2 | ยี่สิบบาทค่ะ / yîi sìp bàat khâ / Twenty baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers line 3 | ขอบคุณครับ / khɔ̀ɔp khun khráp / Thank you. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food line 1 | ขอข้าวหนึ่งจานครับ ไม่เผ็ดครับ / khɔ̌ɔ khâao nʉ̀ng jaan khráp mâi phèt khráp / One plate of rice, please. Not spicy, please. | Non-spicy request attached to plain rice | ขอข้าวผัดหนึ่งจาน ไม่เผ็ดครับ / khɔ̌ɔ khâao phàt nʉ̀ng jaan mâi phèt khráp / One plate of fried rice, not spicy, please. | Applied as explained in the corrections table. |
| food line 2 | ขอน้ำหนึ่งแก้วครับ / khɔ̌ɔ náam nʉ̀ng kâew khráp / One glass of water, please. | Notation or contextual guidance | ขอน้ำหนึ่งแก้วครับ / khɔ̌ɔ náam nʉ̀ng kɛ̂ɛo khráp / One glass of water, please. | Applied as explained in the corrections table. |
| food line 3 | ยี่สิบบาทค่ะ / yîi sìp bàat khâ / Twenty baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food line 4 | อร่อยครับ ขอบคุณครับ / àrɔ̀i khráp khɔ̀ɔp khun khráp / Delicious. Thank you. | Notation or contextual guidance | อร่อยครับ ขอบคุณครับ / à rɔ̀i khráp khɔ̀ɔp khun khráp / Delicious. Thank you. | Applied as explained in the corrections table. |
| directions line 1 | สวัสดีค่ะ ห้องน้ำอยู่ที่ไหนคะ / sawàt dii khâ hɔ̂ng náam yùu thîi nǎi khá / Hello. Where is the toilet? | Notation or contextual guidance | สวัสดีค่ะ ห้องน้ำอยู่ที่ไหนคะ / sà wàt dii khâ hɔ̂ng náam yùu thîi nǎi khá / Hello. Where is the toilet? | Applied as explained in the corrections table. |
| directions line 2 | ตรงไป แล้วเลี้ยวซ้ายครับ / trong pai láew líao sáai khráp / Go straight, then turn left. | Notation or contextual guidance | ตรงไป แล้วเลี้ยวซ้ายครับ / trong pai lɛ́ɛo líao sáai khráp / Go straight, then turn left. | Applied as explained in the corrections table. |
| directions line 3 | ขอบคุณค่ะ / khɔ̀ɔp khun khâ / Thank you. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping line 1 | สวัสดีค่ะ อันนี้เท่าไหร่คะ / sawàt dii khâ an níi thâo rài khá / Hello. How much is this one? | Notation or contextual guidance | สวัสดีค่ะ อันนี้เท่าไหร่คะ / sà wàt dii khâ an níi thâo rài khá / Hello. How much is this one? | Applied as explained in the corrections table. |
| shopping line 2 | สามสิบบาทครับ / sǎam sìp bàat khráp / Thirty baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping line 3 | เอาอันนี้ค่ะ มีถุงไหมคะ / ao an níi khâ mii thǔng mǎi khá / I’ll take this one. Do you have a bag? | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping line 4 | มีครับ / mii khráp / Yes, we do. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping line 5 | ขอบคุณค่ะ / khɔ̀ɔp khun khâ / Thank you. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |

### Quiz questions and choices

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| greetings question 1 | Which phrase means hello?; choices: สวัสดี, ขอบคุณ, ชื่อ; key: สวัสดี | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| greetings question 2 | Which particle commonly makes a woman’s statement polite?; choices: ค่ะ, คุณ, ผม; key: ค่ะ | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| greetings question 3 | ผม ___ เฟรดดี้ (My name is Freddy) · Romanization: chue; choices: ; key: ชื่อ; accepted roman: chue | Pronunciation hint differs from teaching convention | ผม ___ เฟรดดี้ (My name is Freddy) · Romanization: chʉ̂ʉ; choices: ; key: ชื่อ; accepted roman: chʉ̂ʉ, chue | Canonical hint added; original accepted forms retained. |
| greetings question 4 | ___ ครับ (Thank you) · Romanization: khop khun; choices: ; key: ขอบคุณ; accepted roman: khop khun | Pronunciation hint differs from teaching convention | ___ ครับ (Thank you) · Romanization: khɔ̀ɔp khun; choices: ; key: ขอบคุณ; accepted roman: khɔ̀ɔp khun, khop khun | Canonical hint added; original accepted forms retained. |
| numbers question 1 | ยี่สิบบาท is how much?; choices: 20 baht, 2 baht, 100 baht; key: 20 baht | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| numbers question 2 | Which means two?; choices: หนึ่ง, สอง, สาม; key: สอง | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| numbers question 3 | สิบ ___ (Ten baht) · Romanization: baht; choices: ; key: บาท; accepted roman: baht | Pronunciation hint differs from teaching convention | สิบ ___ (Ten baht) · Romanization: bàat; choices: ; key: บาท; accepted roman: bàat, baht | Canonical hint added; original accepted forms retained. |
| numbers question 4 | ___ ครับ (How much?) · Romanization: thao rai; choices: ; key: เท่าไหร่; accepted roman: thao rai | Pronunciation hint differs from teaching convention | ___ ครับ (How much?) · Romanization: thâo rài; choices: ; key: เท่าไหร่; accepted roman: thâo rài, thao rai | Canonical hint added; original accepted forms retained. |
| food question 1 | What does ไม่เผ็ด mean?; choices: Not spicy, Very spicy, Coffee; key: Not spicy | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| food question 2 | Choose the classifier for a glass of water.; choices: แก้ว, จาน, บาท; key: แก้ว | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| food question 3 | ___ น้ำหนึ่งแก้วครับ (May I have a glass of water?) · Romanization: kho; choices: ; key: ขอ; accepted roman: kho | Pronunciation hint differs from teaching convention | ___ น้ำหนึ่งแก้วครับ (May I have a glass of water?) · Romanization: khɔ̌ɔ; choices: ; key: ขอ; accepted roman: khɔ̌ɔ, kho | Canonical hint added; original accepted forms retained. |
| food question 4 | ขอข้าวหนึ่ง ___ (One plate of rice, please) · Romanization: jan; choices: ; key: จาน; accepted roman: jan | Pronunciation hint differs from teaching convention | ขอข้าวหนึ่ง ___ (One plate of rice, please) · Romanization: jaan; choices: ; key: จาน; accepted roman: jaan, jan | Canonical hint added; original accepted forms retained. |
| directions question 1 | เลี้ยวขวา means …; choices: Turn right, Turn left, Go straight; key: Turn right | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| directions question 2 | Which word means near?; choices: ใกล้, ไกล, ไป; key: ใกล้ | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| directions question 3 | ห้องน้ำ ___ คะ (Where is the toilet?) · Romanization: yu thi nai; choices: ; key: อยู่ที่ไหน; accepted roman: yu thi nai | Pronunciation hint differs from teaching convention | ห้องน้ำ ___ คะ (Where is the toilet?) · Romanization: yùu thîi nǎi; choices: ; key: อยู่ที่ไหน; accepted roman: yùu thîi nǎi, yu thi nai | Canonical hint added; original accepted forms retained. |
| directions question 4 | ___ แล้วเลี้ยวซ้าย (Go straight, then turn left) · Romanization: trong pai; choices: ; key: ตรงไป; accepted roman: trong pai | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| shopping question 1 | How do you politely decline?; choices: ไม่เอาค่ะ, เอาอันนี้ค่ะ, มีค่ะ; key: ไม่เอาค่ะ | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| shopping question 2 | สามสิบบาท means …; choices: 30 baht, 3 baht, 13 baht; key: 30 baht | No clear error identified | Retained | Answer key and distractors are appropriate; no change to scoring. |
| shopping question 3 | มีถุง ___ คะ (Do you have a bag?) · Romanization: mai; choices: ; key: ไหม; accepted roman: mai | Pronunciation hint differs from teaching convention | มีถุง ___ คะ (Do you have a bag?) · Romanization: mǎi; choices: ; key: ไหม; accepted roman: mǎi, mai, mái | Canonical hint added; original accepted forms retained. |
| shopping question 4 | เอา ___ ค่ะ (I’ll take this one) · Romanization: an ni; choices: ; key: อันนี้; accepted roman: an ni | Pronunciation hint differs from teaching convention | เอา ___ ค่ะ (I’ll take this one) · Romanization: an níi; choices: ; key: อันนี้; accepted roman: an níi, an ni | Canonical hint added; original accepted forms retained. |

### Patterns objectives and scenarios

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| greetings pattern | ผม / ฉัน + ชื่อ + name = My name is … . คุณชื่ออะไร = What is your name? | Notation or contextual guidance | ผม / ฉัน + ชื่อ + name = My name is … . คุณชื่ออะไร = What is your name? ฉัน is familiar; ดิฉัน is a more formal feminine option. ครับ can end statements or questions; use ค่ะ for statements and คะ for questions in the feminine polite style. | Applied as explained in the corrections table. |
| greetings objectives | Say hello and thank you / Introduce yourself and ask a name / Choose a polite particle | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| greetings scenario | Meet a new neighbor. Greet them, exchange names, and thank them. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers pattern | Item + เท่าไหร่ + polite particle = How much is the item? Number + บาท = price in baht. สิบเอ็ด = 11; ยี่สิบเอ็ด = 21. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers objectives | Recognize useful numbers / Ask a price politely / Understand a price in baht | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| numbers scenario | You are at a market. Ask prices and buy two items. Reuse hello and thank you. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food pattern | ขอ + item + number + classifier + ครับ / ค่ะ. ไม่ + adjective negates it. Reuse หนึ่ง and บาท. | Notation or contextual guidance | ขอ + item + number + classifier + ครับ / ค่ะ. ข้าวผัด (khâao phàt) = fried rice. ไม่เผ็ด means not spicy, not slightly spicy. แก้ว counts drinks served by the glass; จาน counts platefuls of food, not empty plates. Reuse หนึ่ง and บาท. | Applied as explained in the corrections table. |
| food objectives | Order rice and water / Specify quantity with a classifier / Request mild food | Notation or contextual guidance | Order fried rice and water / Specify quantity with a classifier / Request non-spicy food | Applied as explained in the corrections table. |
| food scenario | Order rice and a drink at a café. Ask for non-spicy food, then ask the price. | Notation or contextual guidance | Order fried rice and a drink at a café. Ask for non-spicy food, then ask the price. | Applied as explained in the corrections table. |
| directions pattern | Place + อยู่ที่ไหน + ครับ / คะ = Where is the place? แล้ว = then. ใกล้ (falling) and ไกล (mid) differ in tone and meaning. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions objectives | Ask where a place is / Understand left, right, and straight ahead / Confirm directions politely | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions scenario | Ask a local for the toilet and a café. Repeat the directions to check your understanding. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping pattern | มี + item + ไหม = Do you have …? เอา + item = I’ll take … . ไม่เอา + ครับ / ค่ะ = No, thank you. สามสิบ = 30. | Notation or contextual guidance | มี + item + ไหม = Do you have …? เอา + item = I’ll take … . ไม่เอา + ครับ / ค่ะ = I do not want it (a direct refusal, softened by the particle). Add ขอบคุณ to thank the listener. อันนี้ is a generic this one; use the appropriate classifier when naming a specific kind of object. สามสิบ = 30. | Applied as explained in the corrections table. |
| shopping objectives | Ask for an item and its price / Say what you want or decline politely / Combine greetings, numbers, and requests | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| shopping scenario | Buy something at a neighborhood shop. Ask the price, choose an item, request a bag, and say thank you. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |

### Course roadmaps

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| A1 Beginner | Greet people politely / Handle prices, meals, directions, and shopping | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| A2 Elementary | Talk about daily routines and time / Arrange transport and accommodation / Describe past experiences with แล้ว | Notation or contextual guidance | Talk about daily routines and time / Arrange transport and accommodation / Describe completed actions and changed situations with แล้ว (not a general past-tense marker) | Applied as explained in the corrections table. |
| B1 Intermediate | Tell connected stories / Explain health needs and solve travel problems / Give reasons using เพราะ and discuss plans | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| B2 Advanced | Discuss current affairs and viewpoints / Use formal and informal registers appropriately / Support an opinion and negotiate solutions | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |

### Curriculum tone examples

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| Mid | Mid / มา / maa / come / Keep your pitch level. | No clear error identified | Retained | Tone, pronunciation and gloss retained. Pitch instruction is schematic, not a measured contour. |
| Low | Low / ข่า / khàa / galangal / Use a low pitch. | No clear error identified | Retained | Tone, pronunciation and gloss retained. Pitch instruction is schematic, not a measured contour. |
| Falling | Falling / ข้าว / khâao / rice / Start high and fall. | No clear error identified | Retained | Tone, pronunciation and gloss retained. Pitch instruction is schematic, not a measured contour. |
| High | High / ม้า / máa / horse / Use a high pitch. | No clear error identified | Retained | Tone, pronunciation and gloss retained. Pitch instruction is schematic, not a measured contour. |
| Rising | Rising / หมา / mǎa / dog / Start low and rise. | No clear error identified | Retained | Tone, pronunciation and gloss retained. Pitch instruction is schematic, not a measured contour. |

### Speaking and listening tone examples

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| mid | ดี / dii / Good; Keep your pitch around the middle of your comfortable range.; contour 20,55 65,55 110,55 155,55 | No clear error identified | Retained | Correct lexical tone assignment retained; teacher/TTS contour review is still needed. |
| low | สี่ / sìi / Four; Begin below the middle and let your pitch settle lower.; contour 20,65 65,80 110,85 155,85 | No clear error identified | Retained | Correct lexical tone assignment retained; teacher/TTS contour review is still needed. |
| falling | ใช่ / châi / Yes / correct; Start relatively high, then drop toward the bottom of your range.; contour 20,35 65,25 110,60 155,85 | No clear error identified | Retained | Correct lexical tone assignment retained; teacher/TTS contour review is still needed. |
| high | ซ้าย / sáai / Left; Start above the middle and move toward a higher pitch.; contour 20,50 65,45 110,25 155,20 | No clear error identified | Retained | Correct lexical tone assignment retained; teacher/TTS contour review is still needed. |
| rising | ขวา / khwǎa / Right; Begin low, dip slightly, then rise.; contour 20,70 65,85 110,60 155,25 | No clear error identified | Retained | Correct lexical tone assignment retained; teacher/TTS contour review is still needed. |

### Speaking and listening conversations

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| greeting | สวัสดีครับ / sawàt dii khráp / Hello (polite); options: Hello (polite), Thank you, Goodbye for now | Notation or contextual guidance | สวัสดีครับ / sà wàt dii khráp / Hello (polite); options: Hello (polite), Thank you, Excuse me | Applied as explained in the corrections table. |
| introduction | ผมชื่อเฟรดดี้ครับ / phǒm chʉ̂ʉ Freddy khráp / My name is Freddy; options: My name is Freddy, What is your name?, I am fine | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| food | ขอน้ำหนึ่งแก้วครับ / khɔ̌ɔ náam nʉ̀ng kâew khráp / One glass of water, please; options: One glass of water, please, Two coffees, please, Not spicy, please | Notation or contextual guidance | ขอน้ำหนึ่งแก้วครับ / khɔ̌ɔ náam nʉ̀ng kɛ̂ɛo khráp / One glass of water, please; options: One glass of water, please, Two coffees, please, Not spicy, please | Applied as explained in the corrections table. |
| shopping | อันนี้เท่าไหร่คะ / an níi thâo rài khá / How much is this one?; options: How much is this one?, I do not want a bag, I will take that one | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| directions | ห้องน้ำอยู่ที่ไหนคะ / hɔ̂ng náam yùu thîi nǎi khá / Where is the toilet?; options: Where is the toilet?, Turn right, Go straight | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |

### Vocabulary example overrides

| Location | Original | Issue | Correction or decision | Explanation |
| --- | --- | --- | --- | --- |
| ขอบคุณ | ขอบคุณครับ / khɔ̀ɔp khun khráp / Thank you. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| ฉัน | ฉันชื่อแอนค่ะ / chǎn chʉ̂ʉ Ann khâ / My name is Ann. | Notation or contextual guidance | ฉันชื่อแอนค่ะ / chǎn chʉ̂ʉ ɛɛn khâ / My name is Ann. | Applied as explained in the corrections table. |
| หนึ่ง | หนึ่งบาทครับ / nʉ̀ng bàat khráp / One baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| สอง | สองบาทครับ / sɔ̌ɔng bàat khráp / Two baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| สาม | สามบาทครับ / sǎam bàat khráp / Three baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| สิบ | สิบบาทครับ / sìp bàat khráp / Ten baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| ร้อย | หนึ่งร้อยบาทครับ / nʉ̀ng rɔ́ɔi bàat khráp / One hundred baht. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| กาแฟ | ขอกาแฟหนึ่งแก้วค่ะ / khɔ̌ɔ gaa fae nʉ̀ng kâew khâ / One cup of coffee, please. | Notation or contextual guidance | ขอกาแฟหนึ่งแก้วค่ะ / khɔ̌ɔ kaa fɛɛ nʉ̀ng kɛ̂ɛo khâ / One cup of coffee, please. | Applied as explained in the corrections table. |
| เลี้ยวขวา | เลี้ยวขวาครับ / líao khwǎa khráp / Turn right. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| ใกล้ | ห้องน้ำอยู่ใกล้ค่ะ / hɔ̂ng náam yùu klâi khâ / The toilet is nearby. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| ไกล | ห้องน้ำอยู่ไกลค่ะ / hɔ̂ng náam yùu klai khâ / The toilet is far away. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| ไม่เอา | ไม่เอาถุงค่ะ / mâi ao thǔng khâ / I do not want a bag. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| อันนั้น | เอาอันนั้นค่ะ / ao an nán khâ / I will take that one. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |
| ได้ | ได้ครับ / dâai khráp / Okay. | No clear error identified | Retained | Meaning and structure fit this exercise; qualifications above apply. |

### Generated vocabulary cards

All 40 generated cards were checked against the 40 word entries above and their selected example. The 14 initial explicit overrides are listed above (there are now 16); other examples are taken from the corresponding dialogue by substring matching. This means the corrected fried-rice line also becomes the example for ข้าว, จาน and ไม่เผ็ด. Substring matching is not a semantic validator, but the initial selected examples contained the intended word in a compatible sense. The latest reviewed ใกล้ example deliberately uses the separately labeled contextual expression แถวนี้. Existing personal saved cards are not part of this generated catalog.
