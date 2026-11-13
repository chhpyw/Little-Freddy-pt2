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
  let saved;
  let request;
  const context = vm.createContext({
    URL, FormData: class {},
    location: {hash: '#tutor'},
    window: {addEventListener() {}, confirm() { throw Error('Unexpected confirmation'); }},
    sessionStorage: {getItem() { return null; }, setItem(key, value) { saved = JSON.parse(value); }},
    document: {
      getElementById: $, createElement(tag) { return new Node(tag); },
      querySelector() { return {textContent: 'AI Thai Tutor'}; },
      querySelectorAll(selector) { return selector === '.page' ? sections : []; }
    },
    async fetch(url, options) {
      request = {url, ...options};
      if (pendingFailure) throw Error('Network disconnected');
      return {ok: true, async json() { return {response: '<img src=x onerror=alert(1)> สวัสดี', doc_sources: ['thai.pdf'], web_sources: ['javascript:alert(1)', 'https://example.com/thai'], warnings: ['Model quality warning']}; }};
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
  assert.equal(reply.textContent, '<img src=x onerror=alert(1)> สวัสดี');
  const links = reply.children[0].children;
  assert.equal(links.length, 2); // Document and HTTPS citation; unsafe web URL was discarded.
  assert.equal(links[0].href, '/uploads/thai.pdf');
  assert.equal(links[1].href, 'https://example.com/thai');
  assert.equal(links[1].rel, 'noopener noreferrer');
  assert.equal($('chat-status').textContent, 'Model quality warning');
  assert.equal($('send-btn').disabled, false);
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
  console.log('Tutor UI checks passed: settings, history, safe rendering/citations, warnings, draft recovery, and reset.');
}
module.exports = runTests();
if (require.main === module) module.exports.catch((error) => { console.error(error); process.exitCode = 1; });
