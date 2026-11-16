# Thai tutor script validation and live model evaluation

This is the earlier script-safety evaluation. The [current reliability report](tutor-reliability-benchmark.md) supersedes its default-model and unconstrained-example behavior: qwen3.5:4b is now the overridable default and supported beginner examples are curriculum-backed. The script guard and bounded retries described here remain.

The tutor now rejects invalid teaching fields instead of returning the original failed answer. This fixes the path that displayed Burmese as Thai and then recycled it through conversation history. It does **not** make either tested model a reliable Thai teacher.

## Failure and correction

Previously /chat looked for any Thai consonant anywhere in an unstructured response. One Thai character could hide a Burmese paragraph. A failed retry still returned the original answer with a warning, and the browser stored it as assistant history. The frontend safely used textContent, but safe HTML rendering did not establish the language of the text.

Tutor requests now use Ollama's JSON schema format. The server validates the structure and builds display text itself:

| Field | Allowed content and checks |
| --- | --- |
| examples[].thai | At least one Thai consonant, with letters/marks in U+0E00–U+0E7F; ASCII quantities and common punctuation permitted. English words, Myanmar, Khmer, Lao, Chinese and other non-Thai scripts cannot be hidden by Thai padding. |
| examples[].english | English explanation, optionally mentioning Thai; foreign-language quotations belong in language_notes. |
| examples[].romanization | Latin letters and supported combining tone marks, including ɔ/ɛ/ʉ. Thai or other scripts are rejected; a nonempty guide is required when pronunciation is requested. This does not check pronunciation accuracy or enforce every notation convention. |
| explanation | English/Thai discussion, Latin pronunciation and ordinary citations. Other scripts belong in explicitly labeled quotations or document titles. |
| language_notes[] | Explicit language label, quotation and English/Thai explanation. A quote labeled Thai must pass the Thai check. Burmese and other languages can be quoted as themselves, including newer characters not classified by the host's Unicode database. |
| reference_titles[] | Separate document-title strings can use other scripts. These are model-supplied text, not verification that the reference exists. Actual document/web links still come from the existing retrieval metadata. |

Explicit Myanmar blocks are U+1000–U+109F, Extended-A U+AA60–U+AA7F, Extended-B U+A9E0–U+A9FF and Extended-C U+116D0–U+116FF. Khmer U+1780–U+17FF and Khmer Symbols U+19E0–U+19FF are also detected. Character/category checks reject other non-Thai teaching scripts. Bounds, unexpected fields, wrong types, missing examples and unsafe control characters are checked. The ranges follow the [Unicode block list](https://www.unicode.org/Public/UCD/latest/ucd/Blocks.txt). JSON schema generation follows [Ollama structured-output documentation](https://docs.ollama.com/capabilities/structured-outputs).

There are at most two model calls: initial generation plus one corrective retry. The retry identifies the validation problem, retains the learner's messages and reference context, removes every assistant turn, and never includes the rejected candidate. Both attempts retain the selected level/mode, lesson translation preferences, model settings and source context. Generation uses temperature 0.2, a 4096-token context and a 1024-token output cap; Qwen3/Qwen3.5 thinking remains disabled. The existing 60-second service timeout applies per call. Service unavailability returns an error; exhausted script/schema failures return HTTP 502 with code invalid_thai_generation and no response text.

## History and interface behavior

Initial tutor context excludes old/unstructured assistant responses and assistant objects that fail validation. Valid structured history is revalidated and serialized from its fields; a client-supplied rendered content string is never trusted as assistant text. Learner messages are retained, including legitimate wrong-language quotations needed to explain an error. This does not certify the facts or linguistic quality of otherwise script-valid history.

The browser renders structured fields with textContent, not the raw model response. It verifies the response version and example scripts before assigning the “Thai example (script checked only)” label. Language quotations and reference titles are separately labeled. Invalid replies show an error, keep the learner draft and are not saved as assistant history. Session restoration filters old unvalidated assistant messages while preserving learner messages and aligning source links. Session history is not SQLite progress; no learner database migration is involved.

Legacy /chat document-Q&A calls without tutor settings retain their plain-text API behavior. They are not marked as validated Thai and cannot be rendered as a tutor reply by the updated frontend. Retrieval, extraction, embedding, PDF/document source links and safe citation protocols are unchanged.

## Automated results

**77 Python tests passed, 0 failed. All four JavaScript suites passed; all four application scripts parsed; git diff --check passed.** Coverage includes real Burmese မင်္ဂလာပါ, Myanmar extended blocks, Khmer, Lao and other scripts, padding attacks, valid Thai/English mixtures, tone-marked romanization, explicitly labeled foreign quotations and foreign-script titles, malformed JSON, omitted guides, retry bounds, failure errors, clean history, frontend rejection/restoration and safe text rendering. Existing language-content, RAG/citation, persistence, vocabulary and SQLite regressions passed.

Personal progress.sqlite3 retained SHA256 `972f1463afaca9f395bd49f5ac5232c92e16878bfe50b8a054b8bb0d31d9e68c`. Personal uploads remained empty and the personal vector index remained absent. Every live document and conversation below was synthetic and isolated in temporary storage. No personal cards, progress, documents or vector data were deleted. No CSS/layout changes, dependency additions, default model change, commit or push were made in this step.

## Repeated live language checks

Each model ran three repetitions of four cases through the actual Flask route and local Ollama. “Accepted” means HTTP 200 with schema/script-valid fields, **not** accurate teaching. Rejected cases returned HTTP 502 and no teaching response. Earlier exploratory runs are not pooled into these final counts.

| Case | qwen3:1.7b accepted / rejected | qwen3.5:4b accepted / rejected |
| --- | --- | --- |
| Greeting | 3 / 0 | 3 / 0 |
| Ordering non-spicy fried rice | 1 / 2 | 3 / 0 |
| Correcting a prior Burmese reply and ordering water | 1 / 2 | 3 / 0 |
| Explicitly quoting Burmese while teaching Thai separately | 0 / 3 | 0 / 3 |
| Total | **5 / 7** | **9 / 3** |

The current 1.7b model is not reliable for these requirements. It produced mixed-script pronunciation, malformed/truncated JSON and Burmese in Thai or explanation fields. The 4b model followed the schema/script rules more often, but sometimes put Burmese into explanation/Thai fields despite having a separate quotation field. All such detected candidates were rejected. The schema permits legitimate language discussion; these failures show models failing to put it in the appropriate fields.

Accepted outputs still contained errors. For example, qwen3:1.7b glossed ค่ะ as “Hello” and offered ขอให้เป็นน้ำ 1 แก้ว as a water order. The 4b model produced incorrect tone guides and classifier explanations. These candidates use Thai script, so Unicode validation cannot reject them for being wrong Thai. They must not be copied into the authored lessons or vocabulary. No native verification or comprehensive factual/linguistic evaluation was performed.

Raw results include actual attempts, rejection reasons and returned responses: [qwen3:1.7b](live-language-qwen3-results.json), [qwen3.5:4b](live-language-qwen35-results.json). These are diagnostic records containing rejected text, not teaching resources. Median request times were approximately 5.36s and 12.23s respectively, including retries where used; these are small-sample local observations.

## Live PDF and RAG checks

| Check | qwen3:1.7b | qwen3.5:4b |
| --- | --- | --- |
| Model availability and 768-dimensional embedding | Passed | Passed |
| Intermediate / Free Chat script/schema smoke | Passed | Passed |
| Two-chunk synthetic Thai text re-index and cleanup | Passed | Passed |
| Synthetic PDF extraction/upload | Passed | Passed |
| Explicit PDF answer with price and filename citation | Rejected by teaching-field validation | Passed |
| Semantic PDF answer with price and filename citation | Rejected by teaching-field validation | Passed |
| Synthetic PDF re-index and cleanup | Passed | Passed |
| Total | **8 passed, 2 failed** | **10 passed, 0 failed** |

The default model's two failed end-to-end answers are real failures, not green RAG results. Document extraction and indexing worked; generation failed the new contract and was blocked. The alternative's answers included 37, freddy-smoke.pdf and matching source metadata, but their romanization and explanatory accuracy still need review. Raw evidence: [default-model RAG run](live-script-rag-qwen3-results.json), [alternative-model RAG run](live-script-rag-qwen35-results.json). The earlier pre-fix audit results describe a different acceptance policy and do not supersede these results.

## Hardware compatibility and recommendation

Read-only hardware checks reported an Apple M4 Pro, arm64, Mac16,8 and 24 GiB physical memory. Ollama reported version 0.40.16. The default qwen3:1.7b is GGUF Q4_K_M; the installed qwen3.5:4b is approximately 3.97 GB of NVFP4 weights with the MLX runner. No models were downloaded. Actual successful 4096-context structured calls on this Mac establish runtime compatibility more directly than a parameter-count estimate. Available memory still depends on other applications and context size.

**Recommended local candidate for further evaluation: the already-installed qwen3.5:4b**, which performed better on script/schema compliance and completed both PDF/citation checks here. Its installed tag/runner matches the [official Ollama qwen3.5:4b listing](https://ollama.com/library/qwen3.5:4b). This is not a recommendation to trust its translations, tones or grammar without review. Neither tested model qualifies as a verified Thai teacher. The default was deliberately left unchanged; choose the alternative only after reviewing its outputs:

```sh
CHAT_MODEL=qwen3.5:4b PORT=5055 .venv/bin/python app.py
```

Changing only CHAT_MODEL does not require rebuilding embeddings or changing SQLite. Restart Flask and refresh the page to load the new server/frontend contract. Existing old assistant session messages will be filtered rather than reused.

## Reproduction

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/navigation.test.js
node tests/app.test.js
node tests/speech.test.js
node tests/vocabulary.test.js
.venv/bin/python scripts/live_tutor_language.py --model qwen3:1.7b --repeats 3 --report /tmp/qwen3-language.json
.venv/bin/python scripts/live_tutor_language.py --model qwen3.5:4b --repeats 3 --report /tmp/qwen35-language.json
.venv/bin/python scripts/live_ollama_smoke.py --model qwen3:1.7b --tutor-level Intermediate --report /tmp/qwen3-rag.json
.venv/bin/python scripts/live_ollama_smoke.py --model qwen3.5:4b --tutor-level Intermediate --report /tmp/qwen35-rag.json
```

Live generation is nondeterministic; future acceptance counts can differ. Broader model benchmarking, linguistic grading by a qualified Thai teacher, native pronunciation/audio assessment and visual browser QA remain outstanding. Passing Unicode or schema checks proves none of those.
