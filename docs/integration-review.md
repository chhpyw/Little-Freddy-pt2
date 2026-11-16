# Final integration review

Review session: 13–14 November 2026, Asia/Bangkok. The repository's tracked and
untracked application source, templates, styles, scripts, tests, documentation,
requirements, ignore rules, and repository instructions were inspected before
production changes. Existing changes were retained; nothing was pushed or committed.

## Results

| Check | Result | Evidence and limits |
| --- | --- | --- |
| Python automated tests | 56 passed, 0 failed | `python -m unittest discover -s tests -v`; temporary storage and mocked model calls except explicit live script |
| JavaScript suites | 4 passed, 0 failed | Navigation (11 cases), tutor UI, speech adapters, vocabulary UI; executed using the provided Node runtime because standalone `node` was absent from shell PATH |
| JavaScript syntax | All 4 application scripts parsed | Node VM compile check |
| Dependencies | Passed | `python -m pip check`: no broken requirements in existing environment |
| Whitespace | Passed | `git diff --check` |
| Live Ollama, repeated final run | 17 passed, 1 failed | [Raw synthetic-check results](integration-live-results.json); real local HTTP calls |
| Browser UI / responsive visuals | Not verified | Chrome extension control failed; native fallback was interrupted. CSS breakpoints, template references, and fixture-based navigation were reviewed, not visually certified |
| Real microphone / audible Thai TTS | Not tested | Mock API coverage does not establish microphone capture, recognition quality, or audible playback on this device |
| Live optional web search | Not tested | Backend compatibility is required; unavailable results produce a warning |

The Python suite initially had 32 passing tests. The first added integration batch
reproduced 13 failures; fixes and further regressions bring the total to 56 passing.
The intentional malformed-PDF, storage-error, and partial-reindex tests emit error
messages as fixtures; those log messages are not failed tests. One newly added test
fixture initially lacked a Flask application context; that fixture was corrected.

Live checks used only synthetic prompts and a generated PDF in temporary directories,
not the existing document collection or learner database. The test-only server was
stopped. A read-only fingerprint comparison of the existing default index, learner
database, and document files reported zero changes during the final checks.

## What was verified

- **Dashboard:** combined feature flow checks real lesson, speaking, and vocabulary
  totals; empty states; accuracy math; recommendation evidence; no sample statistics.
- **Tutor:** all three levels and four modes passed request/prompt/history contract
  tests. The live run exercised all 12 combinations and checked for actual Thai
  script in a nonempty response. This is a smoke test, not a linguistic review of
  level appropriateness, grammar, translations, or pedagogy.
- **RAG:** real PDF/DOCX extraction, Markdown/text, chunking, mocked extraction→embedding
  →retrieval→citation→deletion flows, explicit filename and semantic retrieval,
  malformed dimensions, partial embedding failure, duplicate and concurrent uploads,
  index corruption, and write rollback. Live nomic embeddings had 768 dimensions.
  The generated PDF's price (37 baht) appeared in both final retrieval responses,
  with the filename in both source metadata and the actual model answer.
- **Lessons:** five A1 lessons, objectives/vocabulary/dialogues, answer-key exclusion
  from lesson API, multiple choice and fill-ins, server scoring, 75% threshold,
  successful completion, retries that retain best scores, and lesson AI context.
- **Speaking/listening:** five tone guides, ten items/twenty activity states,
  text-only matching that preserves Thai marks, persisted attempts, idempotency,
  conflicting concurrent requests, and mocked voice/recognition failures, cancellation,
  stale events, permission denial, and timeouts.
- **Vocabulary:** lesson/manual saves, examples and categories, duplicate protection,
  due boundaries and overdue reviews, SM-2 intervals/ease/lapses/mastery, review
  history, stale-tab rejection, retry idempotency, accuracy, and recommendations.
- **Persistence:** additive legacy-database migrations, repeated connections, concurrent
  writes, and a fresh Python process reopening saved learner data.
- **Security:** cross-site mutation rejection, trusted loopback hosts, unsafe filename
  aliases and symlinks, safe model text rendering and citation protocols, schema/input
  validation, sanitized service/storage errors, upload limits, response headers, and
  ignore coverage for runtime data and secrets. These are regression checks, not a
  penetration test or proof of security for public deployment.

## Bugs fixed

1. Uploads previously overwrote existing files before extraction/embedding succeeded.
   Uploads now stage privately and duplicate names return 409.
2. Partial embedding success previously published incomplete document indexes. Every
   chunk must now succeed; failed new uploads are removed without touching originals.
3. Failed extraction left new orphan files. Staged files now clean up in `finally`.
4. Index writes could leave partial JSON or silently replace a corrupt index. Writes
   now use atomic replacement; invalid index data returns a non-destructive error.
5. Concurrent index updates could lose document entries. Single-process writers use
   a shared lock. Upload/delete index-write failures preserve existing document data.
6. A filename such as `.pdf` lost its extension during sanitization and crashed
   extraction. Sanitized names are validated; document endpoints reject aliases and
   symlink entries rather than silently mapping them to other files.
7. Malformed/mismatched embedding vectors and malformed model/web payloads could
   crash chat or leak Python exception details. Validation and JSON errors replace
   these paths; missing retrieval and missing Thai script produce explicit warnings.
8. String values such as `"false"` were accepted as truthy settings. Boolean settings
   are validated. Oversize requests and storage errors now return useful JSON.
9. Cross-site mutations and arbitrary Host headers were accepted; local origin/host
   checks and security response headers now guard the personal workspace. Debug is
   disabled in the normal launch path.
10. Speaking UUID variants and concurrent conflicting submissions could bypass retry
    expectations. Canonical UUIDs and a serialized transaction protect attempts.
11. Database schema setup errors could bypass connection cleanup. Schema setup now
    sits inside the existing connection's `try/finally`.
12. Re-indexing could replace complete old chunks with partial new embeddings. Failed
    documents now keep their previous index. Run reindexing with Flask stopped.
13. Default Qwen3 thinking caused observed 60-second timeouts. Optional thinking is
    disabled for Qwen3 chat requests. The repeated live run returned all 12 tutor
    HTTP responses and both PDF answers without those timeouts.

README now includes the overview, actual feature scope, technology stack,
installation, model requirements, launch/configuration, backups, tests, and
troubleshooting. `.gitignore` covers environments, documents, vector indexes,
learner databases and sidecars, and common secret files. No user data was deleted.

## Remaining failures and limitations

The original live run had 6 failed checks out of 18: four tutor responses omitted
Thai, one tutor request timed out, and explicit PDF chat timed out. After disabling
optional Qwen3 thinking, the repeated run had **one remaining content failure**:
Intermediate / Free Chat returned HTTP 200 but no Thai script. All 12 requests
completed, 11 contained Thai, and all final PDF/RAG checks passed. The test was not
weakened to hide that failure. The application now warns about an English-only
response; that warning path is covered by automated tests. Model behavior remains
nondeterministic, and the warning is not a guarantee of good Thai instruction.

Other limits:

- A2–B2 are roadmaps/guided practice; full scored courses remain future work.
- No OCR is built in. Scanned, encrypted, malformed, or unusually structured PDFs
  may not extract useful text. Source metadata only identifies retrieved material;
  it does not guarantee the model used it correctly.
- Browser/device support determines TTS, speech rate, microphone and recognition.
  There is no acoustic tone analysis or pronunciation accuracy measurement.
- Progress belongs to this one personal workspace. There are no separate users,
  authentication, or public deployment guarantees.
- The JSON vector store supports one writer process. Threaded writes are serialized,
  but do not run Flask/reindex/multiple workers simultaneously against it. Atomic
  JSON replacement is not a transaction spanning both the document filesystem and
  index across abrupt process/power failure; preserve backups and rebuild as needed.
- Dependency consistency was checked in the existing virtual environment. A fresh
  installation and the host's standalone Node executable were not tested. The
  existing macOS Python reports urllib3's LibreSSL warning.

## Repeatable commands

Run the application:

```sh
cd /Users/poonyaweeliu/Freddy-Learns-Thai
.venv/bin/python app.py
```

Open `http://127.0.0.1:5000`. Use `PORT=5055 .venv/bin/python app.py` if needed.
Start Ollama separately and install `qwen3:1.7b` and `nomic-embed-text` as described
in [README](../README.md).

Run tests:

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/navigation.test.js
node tests/app.test.js
node tests/speech.test.js
node tests/vocabulary.test.js
.venv/bin/python -m pip check
git diff --check
```

Opt-in live checks (synthetic data; may fail if the model ignores the prompt):

```sh
.venv/bin/python scripts/live_ollama_smoke.py --all-tutor-settings --report /tmp/freddy-live-results.json
```

## Required manual acceptance checks

Use a fresh temporary directory for all mutable acceptance checks, not real learner
storage. This isolates documents, the index, and the database:

```sh
FREDDY_CHECK_DIR="$(mktemp -d /tmp/freddy-manual.XXXXXX)"
FREDDY_UPLOAD_FOLDER="$FREDDY_CHECK_DIR/uploads" \
FREDDY_INDEX_FILE="$FREDDY_CHECK_DIR/index.json" \
FREDDY_PROGRESS_DATABASE="$FREDDY_CHECK_DIR/learner.sqlite3" \
PORT=5055 .venv/bin/python app.py
```

1. Open `http://127.0.0.1:5055` in a desktop browser. Use all six sidebar sections;
   refresh each deep link and try back/forward. Check keyboard focus and no console
   exceptions. Inspect at 1440px desktop, 768px tablet, and 390px mobile widths for
   readable cards, usable forms, no clipped controls or horizontal overflow.
2. For each of the five lessons, toggle translations, choose correct and incorrect
   quiz answers, save words, navigate away and back, and reload. Check dashboard
   totals and recommendations without confusing best scores with latest scores.
3. Try tutor levels and modes with realistic Thai conversation, multiple turns,
   pronunciation preferences, and PDF questions. Judge actual teaching quality,
   not just HTTP success. Stop Ollama and confirm errors preserve drafts.
4. Upload a disposable text PDF with known facts; view it; ask explicit and semantic
   questions; inspect clickable citations. Attempt a duplicate/invalid/scanned PDF.
   Delete only the disposable test document and verify both file and index removal.
5. Follow the [microphone/audio checklist](speaking-listening-testing.md): physically
   listen to Thai TTS at both speeds; record real Thai speech; compare expected and
   recognized text; test denied permission, silence, missing Thai voice, unsupported
   browser, offline service, backgrounding and navigation. Confirm no tone score or
   pronunciation percentage is claimed. Browser recognition may transmit audio to
   its provider; obtain the device user's permission before enabling it.
6. Follow the [vocabulary checklist](vocabulary-spaced-repetition.md): import/add,
   flip/listen, review due cards, test retry/stale-tab behavior, inspect history and
   check mastery/accuracy definitions. Exercise narrow-screen rating buttons.
7. Stop and restart Flask with the same temporary paths. Confirm all progress survives.
   Repeat an audio/recognition check on each target browser/device before release.
