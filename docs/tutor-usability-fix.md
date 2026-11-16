# Tutor usability diagnosis and verification — 16 November 2026

## Observed failure and root cause

The Flask process serving port 5055 had started on 14 November and retained old Python code in memory while serving newer JavaScript from disk. A real HTTP probe returned an unstructured `response` with no `teaching` fields or `script_validation` marker. The frontend correctly rejected that incompatible response. Ollama's log identified qwen3:1.7b for that process, despite the updated source default being qwen3.5:4b. The unstructured reply also contained a semantically incorrect rice expression. Unicode alone would not catch that error.

The original Flask stdout/stderr went to a terminal, with no durable application log to inspect. The user-reported earlier ReadTimeout is consistent with Ollama's recorded 60-second HTTP 500 at 01:41:56 on 16 November; the exact original Flask exception and rejected payload are unavailable. Its underlying cause is not established. Do not conflate that service failure with a language-validation failure.

Before these recovery changes, a fresh isolated Flask HTTP server using the current source and real qwen3.5:4b completed six restaurant turns. One pronunciation turn first failed validation on a quotation labeled Thai and succeeded after retry. That observation establishes a quotation-field validation failure, not that the rejected quotation specifically contained Burmese.

## Changes

- Keep server-side schema and script checks. Classify malformed JSON, schema/field errors, missing Thai, missing requested romanization and wrong-script failures with field paths. Accept English explanations alongside Thai; Myanmar, its extended blocks, Khmer and other inappropriate teaching scripts remain rejected. Precisely wrapped JSON is accepted; arbitrary surrounding prose is rejected.
- Ordinary reviewed beginner replies use a smaller ID-based schema without optional quotation/title generation. Examples, English meanings and pronunciation guides are copied from the reviewed curriculum, not invented by the model. Explicit other-language discussion can still use labeled quotations. Reviewed does not mean native-verified.
- Preserve recent learner context for restaurant follow-ups (water, pronunciation, price and thanks), bound model history, and summarize validated prior examples instead of feeding an incompatible schema back to the model. Corrective retries use learner-only history and never include rejected replies. Validation retries remain bounded at two total attempts.
- If reviewed-context AI commentary fails, return only approved curriculum examples with an explicit **Reviewed lesson fallback** label. No rejected AI commentary or fallback assistant turn enters conversation history. Count fallback usability separately from AI-generation success. Unsupported contexts still return an error after failed validation.
- Separate service timeout/unavailability from language failures. A timeout does not trigger another potentially 60-second request. Supported contexts receive a labeled reviewed fallback; unsupported timeout responses use HTTP 504. The read timeout remains 60 seconds. Empty document indexes no longer trigger unnecessary query embedding.
- Save drafts in session storage, restore them after errors/fallbacks and avoid duplicating a pending learner turn on retry. Retain strict browser validation and safe text rendering. Explain stale-server contract errors explicitly.
- Log request IDs, configured/reported model, elapsed time, token counts, attempt, validation code/field and script family. Logs contain no prompts, raw rejected output, exception text or credentials. Contract/model response headers help identify stale servers. Detect unexpected reported models.

The confirmed stale Flask process alone was restarted on the same port, 5055. Its replacement startup log and real `/chat` response both identify qwen3.5:4b. `/api/ps` also confirmed that model loaded. Model override remains supported. Current runtime log: `/tmp/freddy-flask-5055-20261116.log` (created with owner-only permissions). Refresh the browser to load the updated recovery/draft handling.

## Actual verification

| Check | Actual outcome |
| --- | --- |
| Python unittest discovery | 88 passed, 0 failed; includes RAG/citations, lessons, vocabulary/progress, strict validation and recovery |
| JavaScript | Four suites passed: app, navigation, speech, vocabulary |
| Complete isolated Flask HTTP → real Ollama restaurant dialogue | 6/6 usable; 6 AI commentaries accepted; 0 fallbacks; all first attempts |
| Dialogue coverage | Begin restaurant practice; non-spicy fried rice; water; repeat pronunciation; ask price; closing thanks |
| Live latency | 2.36–6.06 seconds per turn in this run |
| Browser formatter against real HTTP payloads | All six accepted; exact agreement with server formatting |
| Restarted server on 5055 | HTTP 200, validated reviewed reply, reported qwen3.5:4b, one attempt |
| Injected failure tests | Malformed output, genuine Myanmar, missing Thai/romanization, model mismatch, timeout, bounded retry, reviewed fallback and unsupported timeout error passed |
| Browser recovery tests | Draft persistence, refresh restoration, fallback learner-only history, retry deduplication and stale contract handling passed |
| Storage | Existing `progress.sqlite3` SHA-256 unchanged; uploads remained empty; no personal vector index existed |
| Diff whitespace | Passed |

The repeatable [HTTP runner](../scripts/live_restaurant_flow.py) isolates storage and does not mock model generation. [Recorded live results](restaurant-flow-results.json) include the synthetic dialogue, accepted teaching and safe diagnostics. Reproduce with `.venv/bin/python scripts/live_restaurant_flow.py` while Ollama runs. It writes that report only. The separate 5055 probe confirms the actual running backend rather than only a test instance.

Failure recovery was tested with injected service/model failures; the final real Ollama conversation did not time out or require fallback. Browser rendering was checked through JavaScript tests and the actual payload formatter, not a visual browser interaction. Generated commentary can still contain linguistic errors despite valid schema and Unicode. No native verification or comprehensive semantic accuracy is claimed. Source examples retain existing pronunciation/register review limitations. The thank-you reference includes “Delicious” and is labeled with that full meaning; the price example teaches the question rather than inventing a restaurant price. No personal data, lesson design, or vector data was migrated or deleted. No GitHub push was performed.
