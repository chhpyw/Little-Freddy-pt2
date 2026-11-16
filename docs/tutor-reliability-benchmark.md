# Beginner tutor semantic benchmark

Date: 15 November 2026, Asia/Bangkok. This benchmark is human-reviewable and uses the project’s reviewed beginner curriculum. Review is editorial/user review, not independent native verification. The two models ran the same 12 prompts with Beginner / Guided Lesson / pronunciation enabled, isolated storage and one corrective retry at most.

## What is measured

Fixed teaching fields are selected by ID and inserted by the server from the curriculum. Their golden checks cover the requested meaning, quantity, negation, reference point, politeness and pronunciation text. A 12/12 match is a deterministic content/provenance result, not evidence that a model translated correctly. Generated explanations and language notes are screened separately against the case checklists. They remain unreviewed in the app, even when this assistant screening observes no clear error.

Assistant editorial screening is not a native-speaker assessment, a blinded evaluation or a comprehensive fluency grade. “No clear error observed” is not a correctness certificate. The benchmark CLI exit code covers schema acceptance and fixed-field golden matches only; generated-language grading requires review.

## Cases and expected meanings

| Case | Expected Thai | Expected English | Reviewed romanization | Semantic checks |
| --- | --- | --- | --- | --- |
| greetings / greeting | สวัสดีค่ะ คุณชื่ออะไรคะ | Hello. What is your name? | sà wàt dii khâ khun chʉ̂ʉ à rai khá | สวัสดี means hello, not ค่ะ. ค่ะ ends the statement; คะ ends the question. |
| greetings / introduction | ชื่อแอนค่ะ | My name is Ann. (Casual introduction.) | chʉ̂ʉ ɛɛn khâ | ชื่อ means name/be named. Subject omission is natural in context; ฉันชื่อแอนค่ะ remains valid. |
| food / rice | ขอข้าวผัดหนึ่งจาน ไม่เผ็ดนะครับ | One plate of fried rice, not spicy, please. | khɔ̌ɔ khâao phàt nʉ̀ng jaan mâi phèt ná khráp | Exactly one plate; fried rice, not plain rice. ไม่เผ็ด means not spicy, not mildly spicy. จาน counts platefuls; ข้าว is rice, not a classifier. นะครับ softens this request. |
| food / water | ขอน้ำหนึ่งแก้วครับ | One glass of water, please. | khɔ̌ɔ náam nʉ̀ng kɛ̂ɛo khráp | น้ำ is water. หนึ่งแก้ว is one glass serving; no invented ingredients. ขอ requests the item; not a literal ขอให้ construction. |
| directions / near | ห้องน้ำอยู่แถวนี้ค่ะ | The restroom is around here. (Nearby-location reply.) | hɔ̂ng náam yùu thɛ̌ɛo níi khâ | แถวนี้ means around here. Do not gloss the phrase as far from here or change the reference point. |
| directions / far | ห้องน้ำอยู่ไกลจากที่นี่ค่ะ | The restroom is far from here. (Alternative far-location reply.) | hɔ̂ng náam yùu klai jàak thîi nîi khâ | ไกล = far, mid klai; ใกล้ = near, falling klâi. จากที่นี่ = from here, not near here. |
| numbers / twenty | ยี่สิบบาทค่ะ | Twenty baht. | yîi sìp bàat khâ | ยี่สิบ = 20, not 2, 12 or 30. บาท is currency; ค่ะ is not part of the number. |
| numbers / price | สวัสดีค่ะ อันนี้เท่าไหร่คะ | Hello. How much is this one? | sà wàt dii khâ an níi thâo rài khá | อันนี้ = this one, not that one. เท่าไหร่ asks how much; no invented price. คะ is the feminine polite question ending. |
| shopping / decline | ไม่รับถุงค่ะ ขอบคุณค่ะ | I won’t take a bag, thank you. (Alternative when a bag is offered.) | mâi ráp thǔng khâ khɔ̀ɔp khun khâ | Declines, rather than requests, a bag. ไม่รับ = not accepting/taking in this context; ขอบคุณ = thanks. |
| shopping / bag-question | เอาอันนี้ค่ะ มีถุงไหมคะ | I’ll take this one. Do you have a bag? | ao an níi khâ mii thǔng mái khá | มีถุงไหม asks availability, not a refusal. ไหม citation mǎi vs conversational mái; คะ high khá. |
| polite speech / confirmation | ใช่ค่ะ / ใช่ครับ | Yes / correct. (Polite feminine / masculine alternatives.) | châi khâ / châi khráp | ใช่ can confirm yes/correct in context. ค่ะ / ครับ are style alternatives, not both spoken obligatorily. Thai often answers other yes/no questions by repeating the relevant verb. |
| polite speech / particles | เอาอันนี้ค่ะ มีถุงไหมคะ | I’ll take this one. Do you have a bag? | ao an níi khâ mii thǔng mái khá | ค่ะ falling khâ for statement; คะ high khá for question. ไหม citation rising mǎi; conversational high mái. Do not call คะ rising or ค่ะ high. |

The complete exact prompts and independently maintained golden strings are in [tutor_semantic_benchmark.json](../tests/tutor_semantic_benchmark.json). The reusable runner is [benchmark_tutor.py](../scripts/benchmark_tutor.py).

## Final comparison

| Measure | qwen3:1.7b | qwen3.5:4b |
| --- | --- | --- |
| Benchmark requests accepted | 12/12 | 12/12 |
| Fixed examples match expected meaning/source/guide | 12/12 | 12/12 |
| Generated commentary with clear editorial errors | 5/12 | 2/12 |
| Generated commentary needing additional register review | 1/12 | 0/12 |
| No clear commentary error observed in this screening | 6/12 | 10/12 |
| Original repeated script/schema scenarios | 9 accepted, 3 rejected | 9 accepted, 3 rejected |

The repeated script scenarios are greeting, food ordering, correcting prior Burmese output, and discussing Burmese as a quotation while teaching Thai. Each ran three times. Both models passed all first three scenarios; both failed all three language-discussion requests after bounded retries. These were safely rejected with HTTP 502. The fields now have curriculum backing, so these counts are not a direct measure of improved unconstrained translation compared with the older 5/12 and 9/12 baseline.

## Failed and uncertain generated commentary

All fixed examples below remained correct relative to their reviewed goldens. The errors were in separately labeled generated commentary, which can still contradict the fixed material.

| Model and case | Generated issue | Correction or next review |
| --- | --- | --- |
| 1.7b / greeting | Says ค่ะ means hello. | สวัสดี means hello; ค่ะ is a polite statement particle. |
| 1.7b / introduction | Changes the name to แอนน์, inserts unsupported pronunciation and suggests ดิฉัน makes the speaker credible. | Retain ชื่อแอนค่ะ / ฉันชื่อแอนค่ะ. Formality is the relevant ดิฉัน register distinction; pronunciation/name ownership still needs review. |
| 1.7b / water | Introduces ขอ ข้าว หนึ่ง แก้ว and says rice means water here. | น้ำ is water, ข้าว is rice. Use the displayed ขอน้ำหนึ่งแก้วครับ. |
| 1.7b / price | Claims ค่ะ marks truth and untruth. | ค่ะ is a feminine polite statement particle; คะ ends the polite question here. |
| 1.7b / particles | Misidentifies ค่ะ in มีถุงไหมคะ and invents a different bag phrase. | Preserve เอาอันนี้ค่ะ มีถุงไหมคะ, distinguishing statement ค่ะ from question คะ. |
| 1.7b / confirmation | Calls polite alternatives formal and describes women/men ambiguously. | Register and speaker-style review needed; polite does not always mean formal. |
| 4b / bag-question | Calls conversational ไหม falling. | Conversational mái is high; citation-form mǎi is rising. |
| 4b / confirmation | Writes ใช้ค่ะ in commentary. | The confirmation is ใช่ค่ะ; ใช้ means use. |

Additional cautions: the 4b rice commentary drops tone notation in khrap although the fixed guide has khráp. Its explanation of ยี่ as two should not teach that as the ordinary standalone counting word; สอง is used for that. The supplied ยี่สิบ example itself correctly means twenty. These notes do not invalidate accepted contextual variants merely for differing style.

Per-case screening, including all cases with no clear observed error, is recorded in [semantic-benchmark-editorial-review.json](semantic-benchmark-editorial-review.json). Raw final responses: [1.7b semantic run](semantic-benchmark-qwen3-results.json), [4b semantic run](semantic-benchmark-qwen35-results.json). Raw script runs: [1.7b](reliability-qwen3-script-results.json), [4b](reliability-qwen35-script-results.json). Initial exploratory outputs prompted stronger supplied-fact and usage-note grounding; they are not pooled into the final counts.

## Default model and content provenance

The application and live runners now default to qwen3.5:4b. CHAT_MODEL remains an environment override; changing only the chat model does not change the embedding model or require re-indexing. A fresh-process regression test checks both the default and qwen3:1.7b override.

For supported beginner teaching requests, the model selects example_ids from server-supplied curriculum entries. The server inserts their exact Thai, English meaning, pronunciation and reviewed usage notes. The bank has 13 entries drawn from lesson dialogues/overrides and the reviewed polite-confirmation tone guide. It does not let the model create new fixed examples or claim new text has been reviewed. Recognized lesson IDs can supply defaults; topic cues are deliberately narrow. Explicit document/web questions and semantic document questions without a teaching request retain the generated RAG path. A regression test specifically checks that a coffee-price question is not diverted into a fixed coffee lesson just because a retrieved document contains the topic.

The UI distinguishes reviewed curriculum examples/meaning/guides from AI-generated conversation and generated meaning/pronunciation. It says not native-verified, rather than claiming an independent verification that did not occur. Generated explanations, language quotations and reference titles can still be wrong or fabricated. The human-review findings above are not a runtime semantic validator. Existing script rejection, history cleanup, maximum two attempts, translation/pronunciation preferences, modes and levels remain active. Advanced or unsupported conversation remains generated and explicitly unreviewed.

Prompts now supply reviewed vocabulary and usage facts, short spoken-Thai guidance, quantities/negation/reference-point checks, speaker-based politeness, classifier meanings and a consistent pronunciation convention. They prohibit inventing new tone explanations or alternate pronunciation in commentary. The final failed cases show that prompts are still not guarantees.

## RAG and automated regression results

| Check | qwen3:1.7b | qwen3.5:4b |
| --- | --- | --- |
| Live PDF/RAG smoke suite | 8 passed / 2 failed | 10 passed / 0 failed |
| Explicit price answer and filename citation | Rejected by generation validator | Passed |
| Semantic price answer and filename citation | Rejected by generation validator | Passed |
| Embedding, Thai-text re-index, PDF upload/re-index, temporary cleanup | Passed | Passed |

The 1.7b failures were blocked invalid teaching generations, not successful answers. The 4b answers included 37 and freddy-smoke.pdf with matching source metadata; this does not certify their generated pronunciation. Raw final RAG evidence: [1.7b](reliability-qwen3-rag-results.json), [4b](reliability-qwen35-rag-results.json).

**82 Python tests passed, 0 failed. All four JavaScript suites passed; all four application scripts parsed; git diff --check passed.** New tests cover golden meanings/context routing, fixed-field insertion, unknown IDs and invented-field rejection, script failure retry, source-vs-generated labels and mismatches, defaults/overrides, preference handling and explicit/semantic RAG preservation. Existing lesson, vocabulary, SQLite, safe-update, citation and persistence regressions passed. Expected fixture failures in re-index/storage logs are not failed tests.

No authored lesson, vocabulary or speech targets were rewritten in this reliability step. No SQLite schema, review history, learner progress, personal document, vector index or CSS/layout was changed. Personal progress.sqlite3 retained SHA256 `972f1463afaca9f395bd49f5ac5232c92e16878bfe50b8a054b8bb0d31d9e68c`; personal uploads stayed empty and the personal vector index remained absent. Every live check used synthetic conversations/documents and temporary storage. No model was downloaded and nothing was committed or pushed.

Restart Flask and refresh the browser to load the new default and provenance labels. If needed, retain the previous model explicitly:

```sh
CHAT_MODEL=qwen3:1.7b PORT=5055 .venv/bin/python app.py
```

## Human review rubric

For each case, check the whole response, not just its fixed example:

1. Does the Thai express the intended English action, quantity, negation, location and reference point?
2. Is the sentence structure and classifier natural for this situation?
3. Do particles fit the speaker style and statement/question type?
4. Does the English explanation actually describe the displayed Thai?
5. Does romanization preserve syllables, vowel length and lexical tones, including ใกล้/ไกล, คะ/ค่ะ and the two ไหม readings?
6. Does the commentary contradict reviewed material or invent progress, references, rules, ingredients or prices?
7. Are register variants genuinely acceptable in context rather than incorrectly labeled errors?
8. Record reviewer name/qualification and specific corrections before claiming human or native verification.

## Reproduction

```sh
.venv/bin/python scripts/benchmark_tutor.py --model qwen3:1.7b --report /tmp/qwen3-semantic.json
.venv/bin/python scripts/benchmark_tutor.py --model qwen3.5:4b --report /tmp/qwen35-semantic.json
.venv/bin/python scripts/live_tutor_language.py --model qwen3:1.7b --repeats 3 --report /tmp/qwen3-scripts.json
.venv/bin/python scripts/live_tutor_language.py --model qwen3.5:4b --repeats 3 --report /tmp/qwen35-scripts.json
```

Live results are nondeterministic. Topic matching is intentionally narrow and is not general semantic understanding; complex, negated and multi-intent requests need expanded evaluation. Natural conversation outside the supplied beginner bank still uses generated, unreviewed examples. Neither model is a verified Thai teacher.
