'use strict';
// Small device adapters are isolated so browser outcomes can be tested without a microphone.
function recognitionErrorMessage(code) {
  const messages = {
    'not-allowed': 'Microphone permission was denied. Allow microphone access for this site in browser settings, then retry.',
    'service-not-allowed': 'The browser blocked its speech service. Check browser permissions or use another supported browser.',
    'audio-capture': 'No usable microphone was found. Connect one and check your device input settings.',
    'no-speech': 'No speech was detected. Move closer to the microphone and try a short phrase.',
    'network': 'The recognition service could not connect. Check your internet connection and retry.',
    'language-not-supported': 'Thai recognition is unavailable in this browser. Try another browser; listening practice is still available.',
    'aborted': 'Microphone practice cancelled. No transcript was saved.'
  };
  return messages[code] || 'Speech recognition failed. Try again or use a browser with Thai speech recognition support.';
}
class ThaiSpeechAudio {
  constructor(environment) {
    this.environment = environment;
    this.pending = null;
  }
  voices() {
    return this.environment.speechSynthesis?.getVoices().filter((voice) => /^th(?:[-_]|$)/i.test(voice.lang)) || [];
  }
  cancel() {
    if (this.pending) this.pending(false);
    this.environment.speechSynthesis?.cancel();
  }
  play(text, voiceURI, rate) {
    this.cancel();
    const voice = this.voices().find((voice) => voice.voiceURI === voiceURI);
    if (!voice || !this.environment.SpeechSynthesisUtterance) {
      return Promise.reject(new Error('No Thai speech voice is available. Install a Thai voice in your device speech settings, then refresh voices.'));
    }
    return new Promise((resolve, reject) => {
      const utterance = new this.environment.SpeechSynthesisUtterance(text);
      utterance.voice = voice;
      utterance.lang = 'th-TH';
      utterance.rate = rate;
      let finished = false;
      const finish = (played, error) => {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        if (this.pending === finish) this.pending = null;
        if (error) reject(error); else resolve(played);
      };
      const timer = setTimeout(() => {
        finish(false, new Error('Playback did not finish. Check your audio output and try replaying.'));
        this.environment.speechSynthesis.cancel();
      }, 30000);
      this.pending = finish;
      utterance.onend = () => finish(true);
      utterance.onerror = () => finish(false, new Error('Thai audio playback failed. Check the voice and audio output, then replay.'));
      try { this.environment.speechSynthesis.speak(utterance); }
      catch (error) { finish(false, new Error('Your browser could not start Thai speech playback. Try another voice.')); }
    });
  }
}
class ThaiRecognition {
  constructor(environment) {
    this.environment = environment;
    this.current = null;
    this.timer = null;
    this.endCallback = null;
  }
  supported() {
    return !!(this.environment.SpeechRecognition || this.environment.webkitSpeechRecognition) && this.environment.isSecureContext;
  }
  cancel() {
    const current = this.current;
    this.current = null;
    clearTimeout(this.timer);
    if (current) {
      try { current.abort(); } catch { /* Already ended. */ }
    }
    const callback = this.endCallback;
    this.endCallback = null;
    if (callback) callback();
  }
  stop() {
    try { this.current?.stop(); }
    catch { this.cancel(); }
  }
  start(onTranscript, onStatus, onEnd) {
    this.cancel();
    if (!this.supported()) {
      onStatus('Speech recognition is unavailable. Use localhost or HTTPS and a supported browser. You can still study and replay the model audio.');
      onEnd();
      return;
    }
    this.endCallback = onEnd;
    try {
      const Constructor = this.environment.SpeechRecognition || this.environment.webkitSpeechRecognition;
      const recognizer = new Constructor();
      this.current = recognizer;
      this.endCallback = onEnd;
      recognizer.lang = 'th-TH';
      recognizer.continuous = false;
      recognizer.interimResults = false;
      recognizer.maxAlternatives = 1;
      let received = false;
      let failed = false;
      recognizer.onstart = () => { if (this.current === recognizer) onStatus('Microphone is listening. Say the phrase, then press Stop or wait.'); };
      recognizer.onresult = (event) => {
        if (this.current !== recognizer || received || failed) return;
        const result = event.results[event.resultIndex || 0];
        if (!result?.isFinal) return;
        const transcript = result[0]?.transcript?.trim();
        if (transcript) {
          received = true;
          onTranscript(transcript);
          onStatus('Transcript received. Review it, then compare and save. This does not assess pronunciation.');
        }
      };
      recognizer.onerror = (event) => {
        if (this.current !== recognizer) return;
        failed = true;
        onStatus(recognitionErrorMessage(event.error));
        this.cancel();
      };
      recognizer.onnomatch = () => {
        if (this.current !== recognizer) return;
        failed = true;
        onStatus('No clear Thai transcript was returned. Listen again, then retry.');
        this.cancel();
      };
      recognizer.onend = () => {
        if (this.current !== recognizer) return;
        if (!received && !failed) onStatus('No transcript was returned. Try again; Thai recognition may be unavailable.');
        this.current = null;
        clearTimeout(this.timer);
        this.endCallback = null;
        onEnd();
      };
      this.timer = setTimeout(() => {
        if (this.current !== recognizer) return;
        onStatus('Microphone session timed out. Please try a shorter phrase.');
        this.cancel();
      }, 20000);
      recognizer.start();
    } catch {
      onStatus('Could not start the microphone. Check browser permission and microphone availability, then retry.');
      this.cancel();
    }
  }
}

// Interface: no microphone or audio starts until the learner presses a control.
(() => {
  const audio = new ThaiSpeechAudio(window);
  const recognition = new ThaiRecognition(window);
  let content;
  let mode = 'listening';
  let selected;
  let version = 0;
  let heard = false;
  let transcript = '';
  let pendingAttempt;
  let saving = false;
  let completedRows = [];
  function playbackAvailable() { return audio.voices().length > 0 && !!window.SpeechSynthesisUtterance; }
  function refreshVoices() {
    const select = $('thai-voice');
    const previous = select.value;
    select.replaceChildren();
    audio.voices().forEach((voice) => {
      const option = element('option', `${voice.name} · ${voice.lang}`);
      option.value = voice.voiceURI;
      select.append(option);
    });
    if (audio.voices().some((voice) => voice.voiceURI === previous)) select.value = previous;
    const available = playbackAvailable();
    select.disabled = !available;
    $('play-practice').disabled = !available || !!recognition.current;
    document.querySelectorAll('[data-tone-play]').forEach((button) => { button.disabled = !available || !!recognition.current; });
    status('audio-status', available ? 'Browser-generated Thai audio. Slow speed is a request to the voice and may sound less natural.' : 'No Thai voice available. Install a Thai device voice and refresh. Listening attempts stay unavailable; reading and microphone practice remain available.');
  }
  function cancelMedia() {
    const recording = !!recognition.current;
    const playing = !!audio.pending;
    version++;
    audio.cancel();
    recognition.cancel();
    if (recording) {
      transcript = '';
      $('save-speaking').disabled = true;
      status('practice-status', 'Microphone session cancelled. No new transcript was saved.');
    }
    if (playing) status('audio-status', 'Audio stopped. Replay when you are ready.');
    heard = false;
    $('check-listening').disabled = true;
    refreshVoices();
  }
  function showCompletion() {
    const row = completedRows.find((row) => row.item_id === selected?.id && row.mode === mode);
    $('practice-completion').textContent = row ? `${row.completed ? 'Completed' : 'In progress'} · ${row.attempts} saved attempt(s). Completion means ${mode === 'speaking' ? 'a transcript matched the target text' : 'a listening answer was correct'}; it is not a pronunciation qualification.` : 'No saved attempts for this exercise yet.';
  }
  async function loadProgress() {
    const progress = await api('/api/speech/progress');
    completedRows = progress.items;
    $('speech-overview').textContent = `${progress.completed} / ${progress.total} activities completed · ${progress.attempts} attempts. Each word or phrase has a listening activity and a transcript-matching speaking activity.`;
    showCompletion();
  }
  function renderPractice() {
    cancelMedia();
    selected = content.items.find((item) => item.id === $('practice-item').value);
    transcript = '';
    pendingAttempt = null;
    $('recognized-thai').textContent = 'No transcript yet.';
    $('save-speaking').disabled = true;
    $('expected-phrase').hidden = mode === 'listening';
    $('listening-form').hidden = mode !== 'listening';
    $('speaking-controls').hidden = mode !== 'speaking';
    for (const name of ['listening', 'speaking']) {
      $(`${name}-mode`).setAttribute('aria-pressed', String(mode === name));
      $(`${name}-mode`).className = `button ${mode === name ? 'primary' : 'secondary'}`;
    }
    $('practice-topic').textContent = mode === 'listening' && selected.id.startsWith('tone-') ? 'Identify the tone' : selected.topic;
    $('practice-instruction').textContent = mode === 'listening' ? 'Play the audio before answering. Replay as often as you need. Choose the tone for a single-word tone exercise, or the meaning for a conversation.' : 'Listen to the model, then say the expected phrase into your microphone.';
    $('expected-thai').textContent = selected.thai;
    $('expected-roman').textContent = selected.roman;
    $('expected-english').textContent = selected.english;
    $('listening-question').textContent = selected.id.startsWith('tone-') ? 'Which tone did you hear?' : 'What does the phrase mean?';
    $('listening-options').replaceChildren();
    selected.options.forEach((option) => {
      const label = element('label');
      const input = element('input');
      input.type = 'radio'; input.name = 'listening-answer'; input.value = option; input.required = true;
      label.append(input, document.createTextNode(` ${option}`));
      $('listening-options').append(label);
    });
    status('practice-status', '');
    status('practice-feedback', '');
    showCompletion();
  }
  async function play(text, exercise = false) {
    if (recognition.current) return;
    const request = version;
    if (exercise) { heard = false; $('check-listening').disabled = true; }
    status('audio-status', 'Playing browser-generated Thai audio…');
    try {
      const played = await audio.play(text, $('thai-voice').value, Number($('audio-speed').value));
      if (request !== version) return;
      if (played) {
        status('audio-status', 'Playback finished. Replay or change speed any time.');
        if (exercise && mode === 'listening') {
          heard = true;
          $('check-listening').disabled = saving;
        }
      }
    } catch (error) { if (request === version) status('audio-status', error.message, 'error'); }
  }
  function renderTones() {
    content.tones.forEach((tone) => {
      const card = element('article', '', 'card tone-card');
      card.append(element('h3', `${tone.title} tone`), element('p', tone.explanation));
      const figure = element('figure');
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 180 110');
      svg.setAttribute('role', 'img');
      svg.setAttribute('aria-label', `${tone.title} tone: ${tone.explanation} Vertical axis is relative pitch; horizontal axis is time.`);
      const axes = document.createElementNS(svg.namespaceURI, 'path');
      axes.setAttribute('d', 'M15 10 V95 H170'); axes.setAttribute('class', 'pitch-axes');
      const contour = document.createElementNS(svg.namespaceURI, 'polyline');
      contour.setAttribute('points', tone.contour); contour.setAttribute('class', 'pitch-line');
      svg.append(axes, contour);
      figure.append(svg, element('figcaption', 'Pitch ↑ · Time → (illustrative)'));
      const thai = element('strong', tone.thai, 'tone-word'); thai.lang = 'th';
      const playButton = element('button', 'Replay example', 'button secondary');
      playButton.type = 'button'; playButton.dataset.tonePlay = tone.id;
      playButton.onclick = () => play(tone.thai);
      card.append(figure, thai, element('p', `${tone.roman} · ${tone.english}`), playButton);
      $('tone-trainer').append(card);
    });
  }
  async function saveAttempt(response) {
    if (saving || !selected) return;
    const request = version;
    const item = selected;
    if (!pendingAttempt || pendingAttempt.response !== response) {
      pendingAttempt = { item_id: item.id, mode, response, attempt_id: crypto.randomUUID ? crypto.randomUUID() : '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (digit) => (digit ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> digit / 4).toString(16)) };
    }
    saving = true;
    $('check-listening').disabled = true;
    $('save-speaking').disabled = true;
    status('practice-status', 'Saving attempt…');
    try {
      const result = await api('/api/speech/attempts', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(pendingAttempt) });
      if (request === version) {
        status('practice-feedback', `${result.feedback} Expected: ${result.expected}. ${result.limitation}`, result.matched ? 'success' : '');
        status('practice-status', 'Attempt saved. Replay or start a new recording to practice again.');
        if (mode === 'listening') $('expected-phrase').hidden = false;
        transcript = ''; heard = false; pendingAttempt = null;
      }
      try {
        await loadProgress();
        await refreshProgress();
      } catch (error) {
        if (request === version) status('practice-status', 'Attempt saved. Could not refresh progress; reload the page to see updated totals.', 'error');
      }
    } catch (error) {
      if (request === version) {
        status('practice-status', `${error.message} Retry saving; your answer is kept.`, 'error');
        $('check-listening').disabled = !heard;
        $('save-speaking').disabled = !transcript;
      }
    } finally { saving = false; }
  }
  $('listening-form').addEventListener('submit', (event) => {
    event.preventDefault();
    if (!heard) return;
    const answer = new FormData(event.currentTarget).get('listening-answer');
    if (answer) saveAttempt(answer);
  });
  $('save-speaking').onclick = () => { if (transcript && !recognition.current) saveAttempt(transcript); };
  $('start-speaking').onclick = () => {
    if (saving) return;
    audio.cancel();
    transcript = ''; pendingAttempt = null;
    $('recognized-thai').textContent = 'Waiting for a transcript…';
    $('save-speaking').disabled = true;
    $('start-speaking').disabled = true;
    $('stop-speaking').disabled = false;
    status('practice-feedback', '');
    status('practice-status', 'Requesting microphone access…');
    const request = version;
    recognition.start((text) => {
      if (request !== version) return;
      transcript = text;
      $('recognized-thai').textContent = text;
    }, (text) => { if (request === version) status('practice-status', text); }, () => {
      $('start-speaking').disabled = !recognition.supported();
      $('stop-speaking').disabled = true;
      $('save-speaking').disabled = !transcript || saving;
      refreshVoices();
    });
    refreshVoices();
  };
  $('stop-speaking').onclick = () => recognition.stop();
  $('play-practice').onclick = () => { if (selected) play(selected.thai, true); };
  $('stop-audio').onclick = () => {
    audio.cancel();
    status('audio-status', 'Audio stopped. Replay to hear the complete example.');
  };
  $('refresh-voices').onclick = refreshVoices;
  $('thai-voice').onchange = () => { audio.cancel(); heard = false; $('check-listening').disabled = true; };
  $('practice-item').onchange = renderPractice;
  for (const name of ['listening', 'speaking']) {
    $(`${name}-mode`).onclick = () => { if (content) { mode = name; renderPractice(); } };
  }
  window.speechSynthesis?.addEventListener('voiceschanged', refreshVoices);
  function followPracticeLink() {
    const match = location.hash.match(/^#speaking\/([^/]+)\/(listening|speaking)$/);
    if (match && content?.items.some((item) => item.id === match[1])) {
      $('practice-item').value = match[1];
      mode = match[2];
      renderPractice();
    }
  }
  window.addEventListener('hashchange', () => {
    if (!location.hash.startsWith('#speaking')) {
      cancelMedia();
      $('save-speaking').disabled = true;
      transcript = '';
    } else {
      followPracticeLink();
      loadProgress().catch((error) => status('practice-status', error.message, 'error'));
    }
  });
  window.addEventListener('pagehide', cancelMedia);
  document.addEventListener('visibilitychange', () => { if (document.hidden) cancelMedia(); });
  refreshVoices();
  $('start-speaking').disabled = !recognition.supported();
  status('recognition-support', recognition.supported() ? 'Browser recognition is available; Thai service support still depends on your browser/provider.' : 'Microphone transcription is unavailable in this browser or connection. Open on localhost or HTTPS with a supported browser. Model playback and reading remain available.');
  async function initialize() {
    try {
      content = await api('/api/speech');
      content.items.forEach((item) => {
        const option = element('option', item.id.startsWith('tone-') ? 'Tone listening word' : item.topic);
        option.value = item.id;
        // Avoid giving away the answer in tone-listening selector labels.
        if (item.id.startsWith('tone-')) option.textContent += ` ${content.items.indexOf(item) + 1}`;
        $('practice-item').append(option);
      });
      renderTones(); renderPractice(); followPracticeLink();
      await loadProgress();
    } catch (error) { status('practice-status', `${error.message} Reload to retry.`, 'error'); }
  }
  initialize();
})();
