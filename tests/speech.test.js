// Run: node tests/speech.test.js. Device adapters use mocked Web Speech APIs.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/speech.js'), 'utf8');
let timerId = 0;
const timers = new Map();
const context = vm.createContext({
  setTimeout(callback) { timers.set(++timerId, callback); return timerId; },
  clearTimeout(id) { timers.delete(id); }
});
vm.runInContext(source.slice(0, source.indexOf('// Interface:')) + '\nthis.adapters = {ThaiSpeechAudio, ThaiRecognition, recognitionErrorMessage};', context);
const { ThaiSpeechAudio, ThaiRecognition, recognitionErrorMessage } = context.adapters;
async function runTests() {
  let voiceList = [];
  let utterance;
  let cancellations = 0;
  const environment = {
    SpeechSynthesisUtterance: class { constructor(text) { this.text = text; } },
    speechSynthesis: {
      getVoices() { return voiceList; },
      speak(value) { utterance = value; },
      cancel() { cancellations++; }
    }
  };
  const audio = new ThaiSpeechAudio(environment);
  await assert.rejects(audio.play('ดี', '', 1), /No Thai speech voice/);
  voiceList = [{ lang: 'en-US', voiceURI: 'en' }, { lang: 'th-TH', voiceURI: 'thai' }];
  assert.equal(audio.voices().length, 1);
  let playback = audio.play('สี่', 'thai', 0.7);
  assert.equal(utterance.lang, 'th-TH');
  assert.equal(utterance.text, 'สี่');
  assert.equal(utterance.rate, 0.7);
  utterance.onend();
  assert.equal(await playback, true);
  playback = audio.play('ดี', 'thai', 1);
  audio.cancel();
  assert.equal(await playback, false);
  utterance.onend(); // A late event cannot mark interrupted playback successful.
  playback = audio.play('ดี', 'thai', 1);
  utterance.onerror();
  await assert.rejects(playback, /playback failed/);
  playback = audio.play('ดี', 'thai', 1);
  for (const callback of [...timers.values()]) callback();
  await assert.rejects(playback, /did not finish/);
  assert.ok(cancellations > 0);
  assert.equal(new ThaiSpeechAudio({}).voices().length, 0);

  let recognizer;
  let ended = 0;
  let transcript = '';
  let messages = [];
  const recognitionEnvironment = {
    isSecureContext: true,
    webkitSpeechRecognition: class {
      constructor() { recognizer = this; }
      start() { this.onstart(); }
      stop() { this.onend(); }
      abort() { this.aborted = true; }
    }
  };
  const recognition = new ThaiRecognition(recognitionEnvironment);
  const start = () => recognition.start((text) => { transcript = text; }, (text) => messages.push(text), () => ended++);
  assert.equal(recognition.supported(), true);
  start();
  assert.equal(recognizer.lang, 'th-TH');
  assert.equal(recognizer.interimResults, false);
  recognizer.onresult({ results: [{ isFinal: false, 0: { transcript: 'interim' } }] });
  assert.equal(transcript, '');
  recognizer.onresult({ results: [{ isFinal: true, 0: { transcript: ' สวัสดีครับ ' } }] });
  assert.equal(transcript, 'สวัสดีครับ');
  recognition.stop();
  assert.equal(ended, 1);
  assert.equal(recognition.current, null);
  transcript = '';
  start();
  recognizer.onerror({error: 'not-allowed'});
  assert.match(messages.at(-1), /permission was denied/);
  assert.equal(recognition.current, null);
  assert.equal(ended, 2);
  assert.equal(transcript, '');
  start();
  const stale = recognizer;
  recognition.cancel();
  stale.onresult({ results: [{ isFinal: true, 0: { transcript: 'stale result' } }] });
  assert.equal(transcript, '');
  start();
  recognizer.onend();
  assert.match(messages.at(-1), /No transcript/);
  start();
  recognizer.onnomatch();
  assert.match(messages.at(-1), /No clear Thai transcript/);
  start();
  for (const callback of [...timers.values()]) callback();
  assert.match(messages.at(-1), /timed out/);
  assert.equal(recognition.current, null);
  for (const code of ['audio-capture', 'no-speech', 'network', 'language-not-supported', 'service-not-allowed', 'aborted', 'unknown']) {
    assert.ok(recognitionErrorMessage(code).length > 20);
  }
  const unsupported = new ThaiRecognition({ isSecureContext: true });
  assert.equal(unsupported.supported(), false);
  unsupported.start(() => assert.fail('Unexpected transcript'), (text) => assert.match(text, /unavailable/), () => ended++);
  assert.equal(new ThaiRecognition({...recognitionEnvironment, isSecureContext: false}).supported(), false);
  const beforeConstructorFailure = ended;
  const throws = new ThaiRecognition({isSecureContext: true, SpeechRecognition: class { constructor() { throw Error('unavailable'); } }});
  throws.start(() => {}, (text) => assert.match(text, /Could not start/), () => ended++);
  assert.equal(ended, beforeConstructorFailure + 1);
  assert.equal(timers.size, 0);
  console.log('Speech adapter checks passed: voices, rate, replay/cancel, playback errors/timeouts, recognition, permission denial, missing support, no speech, and stale events.');
}
module.exports = runTests();
if (require.main === module) module.exports.catch((error) => { console.error(error); process.exitCode = 1; });
