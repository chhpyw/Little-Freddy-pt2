// Run: node tests/app.test.js. Tutor request/history, failure recovery, and safe text rendering.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/app.js'), 'utf8');
class Node {
  constructor(tag) { this.tag = tag; this.children = []; this.events = {}; this.dataset = {}; this.value = ''; this.checked = true; this.textContent = ''; this.classList = {toggle() {}}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  addEventListener(name, callback) { this.events[name] = callback; }
  setAttribute(key, value) { this[key] = value; }
  removeAttribute(key) { delete this[key]; }
  remove() { this.removed = true; }
  focus() {}
}
async function runTests() {
  const nodes = new Map();
  function $(id) { if (!nodes.has(id)) nodes.set(id, new Node('div')); return nodes.get(id); }
  $('tutor-level').value = 'Beginner'; $('tutor-mode').value = 'Free Chat';
  const sections = ['dashboard', 'tutor', 'learn', 'vocabulary', 'library', 'speaking'].map((id) => ({id}));
  let pendingFailure = false;
  let pendingInvalid = false;
  let pendingLegacy = false;
  let pendingFallback = false;
  let restoreData = null;
  const teaching = {explanation: '<img src=x onerror=alert(1)>', examples: [{thai: 'สวัสดี', english: 'Hello', romanization: 'sà wàt dii'}], language_notes: [], reference_titles: []};
  let saved;
  let request;
  const context = vm.createContext({
    URL, FormData: class {},
    location: {hash: '#tutor'},
    window: {addEventListener() {}, confirm() { throw Error('Unexpected confirmation'); }},
    sessionStorage: {getItem() { return restoreData; }, setItem(key, value) { saved = JSON.parse(value); }},
    document: {
      getElementById: $, createElement(tag) { return new Node(tag); },
      querySelector() { return {textContent: 'AI Thai Tutor'}; },
      querySelectorAll(selector) { return selector === '.page' ? sections : []; }
    },
    async fetch(url, options) {
      request = {url, ...options};
      if (pendingFailure) throw Error('Network disconnected');
      if (pendingLegacy) return {ok: true, async json() { return {response: 'Old unstructured server reply'}; }};
      if (pendingFallback) return {ok: true, async json() { return {
        teaching: {...teaching, explanation: ''}, script_validation: 'thai-fields-v1',
        reviewed_examples: [{id: 'greeting', lesson_id: 'greetings', ...teaching.examples[0]}],
        response_kind: 'reviewed_fallback', ai_commentary_accepted: false,
        warnings: ['Ollama timed out. Showing reviewed lesson examples only.']}; }};
      return {ok: true, async json() { return {response: 'Thai: မင်္ဂလာပါ', teaching: pendingInvalid ? {...teaching, examples: [{thai: 'ก ' + pendingInvalid, english: 'Hello', romanization: 'hello'}]} : teaching,
        script_validation: 'thai-fields-v1', doc_sources: ['thai.pdf'], web_sources: ['javascript:alert(1)', 'https://example.com/thai'], warnings: ['Model quality warning']}; }};
    }
  });
  vm.runInContext(source, context);
  $('user-input').value = 'Explain greetings';
  $('tutor-level').value = 'Advanced'; $('tutor-mode').value = 'Roleplay';
  await $('chat-form').events.submit({preventDefault() {}});
  const body = JSON.parse(request.body);
  assert.equal(request.url, '/chat');
  assert.deepEqual(body.tutor, {level: 'Advanced', mode: 'Roleplay', pronunciation: true});
  assert.equal(saved.messages.length, 2);
  const reply = $('chat-window').children.at(-1);
  assert.match(reply.textContent, /<img src=x onerror=alert\(1\)>/);
  assert.match(reply.textContent, /Generated Thai text \(script checked; language unreviewed\): สวัสดี/);
  assert.doesNotMatch(reply.textContent, /မင်္ဂလာပါ/); // Raw response text is never rendered.
  const links = reply.children[0].children;
  assert.equal(links.length, 2); // Document and HTTPS citation; unsafe web URL was discarded.
  assert.equal(links[0].href, '/uploads/thai.pdf');
  assert.equal(links[1].href, 'https://example.com/thai');
  assert.equal(links[1].rel, 'noopener noreferrer');
  assert.equal($('chat-status').textContent, 'Model quality warning');
  assert.equal($('send-btn').disabled, false);
  for (const script of ['မင်္ဂလာပါ', 'សួស្តី', '\u{116d0}']) {
    pendingInvalid = script;
    $('user-input').value = 'Correct the wrong-language response';
    await $('chat-form').events.submit({preventDefault() {}});
    assert.equal(saved.messages.length, 2);
    assert.equal($('user-input').value, 'Correct the wrong-language response');
    assert.match($('chat-status').textContent, /blocked/);
  }
  pendingInvalid = false;
  teaching.language_notes = [{language: 'Burmese', quote: 'မင်္ဂလာပါ', explanation: 'This is a Burmese quotation, not a Thai example.'}];
  const labeled = vm.runInContext('teachingText', context)(teaching);
  assert.match(labeled, /Language quotation \(Burmese\): မင်္ဂလာပါ/);
  assert.doesNotMatch(labeled, /Generated Thai text[^\n]*မင်္ဂလာပါ/);
  teaching.language_notes = [];
  const format = vm.runInContext('teachingText', context);
  const reviewed = [{id: 'fixture', lesson_id: 'greetings', ...teaching.examples[0], usage: 'A reviewed usage note.'}];
  const fixed = format(teaching, reviewed);
  assert.match(fixed, /Reviewed curriculum example \(greetings; not native-verified\)/);
  assert.match(fixed, /AI-generated conversation \(not language reviewed\)/);
  assert.match(fixed, /Curriculum usage note: A reviewed usage note/);
  assert.throws(() => format(teaching, [{...reviewed[0], english: 'A contradictory meaning'}]), /mismatch/);
  pendingFailure = true;
  $('user-input').value = 'Keep this draft';
  await $('chat-form').events.submit({preventDefault() {}});
  assert.equal($('user-input').value, 'Keep this draft');
  assert.equal(saved.messages.length, 2); // Failed response doesn't pollute history.
  assert.match($('chat-status').textContent, /Network disconnected/);
  assert.equal($('send-btn').disabled, false);
  $('clear-chat').events.click();
  assert.equal(saved.messages.length, 0);
  assert.equal($('user-input').value, '');
  assert.equal($('chat-window').children.length, 1);
  restoreData = JSON.stringify({messages: [
    {role: 'assistant', content: 'Thai: မင်္ဂလာပါ'},
    {role: 'user', content: 'Earlier learner topic'},
    {role: 'assistant', content: 'Thai: မင်္ဂလာပါ', teaching, script_validation: 'thai-fields-v1'}
  ], sources: [{docs: ['old.pdf']}, {}, {docs: ['thai.pdf']}]});
  vm.runInContext('restoreConversation()', context);
  assert.equal($('chat-window').children.length, 2);
  assert.doesNotMatch($('chat-window').children.at(-1).textContent, /မင်္ဂလာပါ/);
  pendingFailure = false;
  pendingLegacy = true;
  $('user-input').value = 'Keep my draft through a stale server error';
  await $('chat-form').events.submit({preventDefault() {}});
  assert.match($('chat-status').textContent, /Restart Flask/);
  assert.equal(saved.messages.length, 2);
  assert.equal(saved.draft, 'Keep my draft through a stale server error');
  restoreData = JSON.stringify(saved);
  $('user-input').value = '';
  vm.runInContext('restoreConversation()', context);
  assert.equal($('user-input').value, saved.draft);
  pendingLegacy = false;
  pendingFallback = true;
  $('user-input').value = 'Teach restaurant ordering';
  await $('chat-form').events.submit({preventDefault() {}});
  assert.equal(saved.messages.length, 3);
  assert.equal(saved.messages.at(-1).role, 'user');
  assert.equal(saved.draft, 'Teach restaurant ordering');
  assert.match($('chat-window').children.at(-1).textContent, /Reviewed lesson fallback/);
  assert.match($('chat-status').textContent, /timed out/);
  assert.equal(saved.messages.filter((message) => message.role === 'assistant').length, 1);
  pendingFallback = false;
  await $('chat-form').events.submit({preventDefault() {}});
  assert.equal(JSON.parse(request.body).messages.length, 3); // No duplicate pending learner turn.
  assert.equal(saved.messages.length, 4);
  assert.equal(saved.sources.length, 4);
  assert.equal(saved.draft, '');
  console.log('Tutor UI checks passed: settings, history, safe rendering/citations, warnings, draft recovery, and reset.');
}
module.exports = runTests();
if (require.main === module) module.exports.catch((error) => { console.error(error); process.exitCode = 1; });
