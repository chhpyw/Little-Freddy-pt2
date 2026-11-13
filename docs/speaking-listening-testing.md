# Speaking & Listening: manual device checks

The automated suite tests database behavior, assessment, navigation, and mocked Web
Speech events. It does not verify a physical microphone, audible voice quality, or
provider availability on your device. Run these checks in a real browser.

## Start without changing personal progress

From the project directory, use a separate SQLite file for manual checks:

```sh
FREDDY_PROGRESS_DATABASE=/tmp/freddy-audio-check.sqlite3 .venv/bin/python app.py
```

Open `http://127.0.0.1:5000/#speaking`. Microphone recognition requires a supported
browser on localhost or HTTPS, a connected microphone, and browser permission.
The browser may send audio to its recognition provider. This app stores transcript
text and practice results in SQLite; it does not record or store microphone audio.
No Ollama model is needed for these exercises.

## Audio and tone trainer

1. Confirm the sidebar section opens and shows five tone cards, Thai examples,
   romanization, and pitch sketches. Use keyboard Tab and Enter to reach controls.
2. Select an installed Thai voice. If voices arrive late, verify they populate
   automatically or press **Refresh voices**. No English voice should be substituted.
3. Play each example. Confirm audible Thai and that **Stop audio** interrupts it.
   Replay at normal and slower speed. Some voices ignore rate changes; do not treat
   slow synthesis as a reference for precise pitch or timing.
4. Confirm the page identifies audio as browser TTS, and diagrams as illustrative.
   The words/tones were checked against [NIU Spoken Thai, Unit 1](https://seasite.niu.edu/thai/spokenthai/unit1/practice/practice.htm).
   No human recording assets are bundled. The source link supports the examples;
   it is not a recording license or a guarantee about a device's synthesized voice.
5. Select a tone listening word. Before playback finishes, **Check and save answer**
   must remain unavailable. The expected Thai/romanization/meaning is hidden until
   feedback. Stopping or failed playback must not count as hearing the exercise.
6. Play to the end, choose an answer, and save. Try both a wrong and correct answer;
   confirm feedback, attempt count, and completion. Replay for a new attempt.
7. Repeat with greetings, introductions, food ordering, shopping, and directions.
8. On a device without a Thai voice (or a browser without speech synthesis), confirm
   an actionable message and disabled replay/listening submission controls. Reading
   and supported microphone practice should remain usable. No attempts should be
   silently created. Install a Thai device voice and refresh to recover.
9. Navigate away during playback and confirm it stops. Test a narrow mobile window:
   cards and controls must fit without horizontal overflow.

## Microphone and recognition

1. Switch to **Speaking**. Confirm expected Thai, romanization, and English appear.
   The page should explain transcript comparison and browser/provider processing.
2. Press **Start microphone**, allow permission, and say a short phrase. Confirm
   the listening indicator, **Stop microphone**, and the final recognized Thai text.
   Compare the displayed text with what you said; recognition may be wrong.
3. Press **Compare transcript and save attempt**. A matching transcript completes
   this text-matching activity. A different transcript gives a retry suggestion.
   Neither outcome should claim measured pronunciation, tone, or fluency accuracy.
4. Start another recording and use **Stop microphone**. If no final transcript is
   returned, no attempt should save and a retry message should appear.
5. Deny permission in a separate browser profile or reset site microphone permission.
   Confirm a useful error, no saved attempt, and a usable retry after permission is
   restored. Also test silence, a missing input device, and a disconnected network.
6. In a browser without SpeechRecognition/webkitSpeechRecognition (or on an insecure
   non-localhost origin), confirm the start control is disabled with an explanation.
   Tone study and supported model playback should still work. Typed responses must
   not be presented as recognized speech.
7. Start recording, then change item, mode, sidebar section, or background the tab.
   Confirm recording stops and late results are not attached to another item.
8. During microphone capture, model replay is unavailable so synthesized speech is
   not fed into the recognizer. Confirm recording ends or times out, then replay
   becomes available again.

## Persistence and retries

1. Complete a listening answer and a matching transcript. Check the dashboard's
   Speaking & Listening count and saved attempts; lesson quiz scores stay unchanged.
2. Reload, then stop and restart Flask with the same test database path. Counts and
   completed activity states must remain. Wrong retries must not erase completion.
3. Stop Flask before saving a transcript, then restart it. Retry saving the kept
   transcript. Repeated delivery of the same attempt must count only once.
4. Recheck existing lesson quizzes, tutor chat, vocabulary cards, and PDF Library.

## Automated checks

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/navigation.test.js
node tests/speech.test.js
```

Node tests use only built-in modules and fake Web Speech APIs. Python tests use
isolated temporary databases and preserve personal lesson/PDF data. The existing
Python environment may emit an urllib3/LibreSSL warning; it is independent of speech
practice and should not be interpreted as a microphone test result.

Browser behavior reference: [MDN SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)
and [MDN getVoices](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices).
