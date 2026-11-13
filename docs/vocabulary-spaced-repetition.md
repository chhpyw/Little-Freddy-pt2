# Vocabulary and spaced repetition

## Reusing existing features

The Vocabulary page replaces the original unsaved eight-card sample. It uses the
existing `LESSONS` vocabulary, the existing `database()` connection manager, the
existing progress endpoint, and the Thai speech adapter added for Speaking &
Listening. There is no separate word database, scheduling service, or paid API.

Lesson word imports copy the lesson's Thai, romanization, and English. Examples
reuse lesson dialogues; a small example supplement covers words not in those
dialogues. Tone-aware romanization is a reading aid; it is not an audio assessment.
Manual entries use the learner's own text and are labeled as personal entries.

The six categories are Greetings, Food, Numbers, Transportation, Shopping, and
Daily Conversations. Filters affect the collection and review session, while
statistics describe all saved words. Audio uses an installed Thai browser voice;
missing voices do not block flashcards or reviews.

## SM-2 daily scheduler

The scheduler follows the interval/ease rules in
[Piotr Wozniak's SM-2 description](https://www-beta.supermemo.com/archives1990-2015/english/ol/sm2),
with explicit daily-review adaptations below.

Each new card starts with ease 2.5, zero successful repetitions, and is due today.
The learner recalls the answer, reveals it, then rates recall from 0–5:

| Rating | Recall |
| --- | --- |
| 0 | Nothing recalled |
| 1 | Incorrect; answer familiar |
| 2 | Incorrect; answer seemed easy |
| 3 | Correct with difficulty |
| 4 | Correct with hesitation |
| 5 | Correct without difficulty |

For ratings 3–5, consecutive successful repetitions increase by one. Intervals are
1 day, then 6 days, then `ceil(previous_interval × previous_ease)`.
Ease becomes `max(1.3, ease + 0.1 − (5 − quality) × (0.08 + (5 − quality) × 0.02))`.

Daily adaptations: a rating below 3 resets the repetition count to zero, schedules
one day later, and also updates ease. The app does not implement SM-2's additional
same-day repetition loop. A practical interval cap of 36,500 days prevents runaway
date arithmetic. Only cards due today or earlier accept scheduled reviews;
browsing does not advance schedules. The next date is relative to the actual
review date, including for overdue cards. Review dates use Bangkok (UTC+7) days;
history timestamps are UTC instants.

For example, three successive ratings of 4 give intervals 1, 6, and 15 days.
An incorrect recall then restarts the sequence with one day. Ease has a 1.3 floor.
The scheduler is deterministic and does not use model output.

## Statistics and recommendations

- **Saved words**: unique saved Thai entries, normalized for Unicode and whitespace.
- **Due**: cards whose scheduled Bangkok date is today or earlier, including new cards.
- **Mastered**: at least three consecutive successful repetitions and a scheduled
  interval of at least 21 days. A lapse removes this status. This is a scheduling
  milestone, not proof of language mastery.
- **Recall accuracy**: number of review ratings 3–5 divided by all reviews. It is
  self-reported recall, separate from quiz scores or speaking transcript matches.
  No reviews displays an empty state rather than an invented percentage.

Recommendations prioritize due reviews, latest quiz scores below 75%, vocabulary
lapses and their source lessons, the next incomplete lesson, and incomplete or
recently mismatched speaking/listening activities. Links open the actual lesson,
due-review session, or selected speaking item and mode. There is no inferred study
time or fabricated streak. Existing lesson completion and best scores keep their
original meanings.

## Persistence and safe migration

All tables live in the existing `PROGRESS_DATABASE`, configured by
`FREDDY_PROGRESS_DATABASE`. Back up that file as usual. Migration version 1 is
recorded in `schema_migrations`; it adds `vocabulary`, `vocabulary_reviews`, and
indexes in one transaction. Existing lesson and speaking tables and rows are
preserved. Repeated startup/requests do not reset vocabulary or history.
Concurrent initial requests are serialized by SQLite.

Saving the same normalized Thai word twice keeps its original content and schedule,
including when a later lesson import encounters a manual entry. Save operations
and review history are committed atomically. Reviews store rating, timestamp,
previous schedule, resulting schedule, and revision. A UUID makes retried delivery
idempotent; a card revision rejects stale reviews from a second tab. Future cards
can be browsed but cannot be rated to artificially inflate their intervals.

This remains one personal learning workspace shared by browsers accessing the
same Flask instance; it does not introduce user accounts.

## Automated and manual verification

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/navigation.test.js
node tests/speech.test.js
node tests/vocabulary.test.js
```

Python tests cover imports, manual saving, validation, duplicates, scheduling,
lapses, mastery, due boundaries, overdue reviews, idempotency, concurrent requests,
legacy schema migration, persistence, statistics, and recommendation evidence.
The dependency-free JavaScript tests exercise flashcard UI handlers with a DOM/API
fixture, category filtering, reveal-before-rating, and network retry handling.
They complement the existing navigation and speech regression tests.

For a manual session, use an isolated database:

```sh
FREDDY_PROGRESS_DATABASE=/tmp/freddy-vocabulary-check.sqlite3 .venv/bin/python app.py
```

1. Open Learn Thai, save one word, then save all lesson words. Repeated saving must
   not increase the count twice. Open Vocabulary and confirm examples and categories.
2. Add a personal word with all example fields. Use Thai script and tone guides.
   Re-add it with surrounding whitespace and confirm its original data is kept.
3. Flip a card with mouse or keyboard. Check Thai, romanization, English, example,
   and audio. Without a Thai voice, expect guidance and working reviews.
4. Start a due review, reveal its answer, then rate recall. Confirm its next date,
   history, due count, and self-rated accuracy. Browse future cards without rating.
5. Check recommendations and the dashboard. Complete or fail a lesson and a speaking
   activity; recommendations should explain the recorded result and open that activity.
6. Reload and restart Flask with the same database; words, schedules, and history
   should persist. Review one card in two tabs; the stale tab must refresh.
7. Interrupt a save by stopping Flask or disconnecting the browser, then retry the
   same rating. A delivered retry must not create a second review history row.
8. At a narrow mobile width, check cards, category selection, manual entry, and all
   rating buttons. Check the same flow on desktop. Actual device audio and visual
   layout still require a browser check; automated fixtures do not verify them.
