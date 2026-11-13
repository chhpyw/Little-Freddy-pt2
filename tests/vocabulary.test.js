// Run: node tests/vocabulary.test.js. Exercises the actual UI handlers with a small DOM/API fixture.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const source = fs.readFileSync(path.join(__dirname, '../static/vocabulary.js'), 'utf8');
class Node {
  constructor(tag = 'div') {
    this.tag = tag; this.children = []; this.dataset = {}; this.events = {};
    this.disabled = false; this.hidden = false; this.value = ''; this.textContent = '';
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = [...children]; }
  setAttribute(key, value) { this[key] = value; }
  addEventListener(key, callback) { this.events[key] = callback; }
}
async function runTests() {
  const nodes = new Map();
  const $ = (id) => { if (!nodes.has(id)) nodes.set(id, new Node()); return nodes.get(id); };
  const events = {};
  const stored = [{id: 1, thai: 'น้ำ', roman: 'náam', english: 'Water', category: 'Food',
    example_thai: 'ขอน้ำครับ', example_roman: 'khɔ̌ɔ náam khráp', example_english: 'Water, please.',
    revision: 0, due_on: '2026-11-13', interval_days: 0, repetitions: 0, lesson_id: 'food'}];
  let reviews = 0;
  let failure = true;
  let progressRefreshes = 0;
  const submissions = [];
  const context = vm.createContext({
    $, crypto: webcrypto, location: {hash: '#vocabulary'}, Date,
    ThaiSpeechAudio: class { voices() { return []; } cancel() {} },
    document: {
      querySelectorAll() { return $('rating-buttons').children; },
      addEventListener() {}
    },
    window: {addEventListener(name, callback) { events[name] = callback; }},
    element(tag, text = '', className = '') { const node = new Node(tag); node.textContent = text; node.className = className; return node; },
    status(id, text, type) { $(id).textContent = text; $(id).className = type; },
    async refreshProgress() { progressRefreshes++; },
    async api(url, options) {
      if (url.endsWith('/catalog')) return {categories: ['Food', 'Greetings'], lessons: [{id: 'food', title: 'Food'}]};
      if (url === '/api/vocabulary') return {
        words: structuredClone(stored), today: '2026-11-13',
        stats: {total: 1, due: reviews ? 0 : 1, mastered: 0, reviews, recalled: reviews, accuracy: reviews ? 100 : null}
      };
      if (url.endsWith('/review')) {
        const body = JSON.parse(options.body); submissions.push(body);
        if (failure) { failure = false; throw Error('Network disconnected'); }
        reviews++;
        Object.assign(stored[0], {revision: 1, due_on: '2026-11-14', interval_days: 1, repetitions: 1});
        return {review: stored[0]};
      }
      if (url.endsWith('/history')) return {history: []};
      throw Error('Unexpected API call: ' + url);
    }
  });
  vm.runInContext(source, context);
  const flush = async () => { for (let i = 0; i < 30; i++) await Promise.resolve(); };
  await flush();
  assert.equal($('flashcard-word').textContent, 'น้ำ');
  assert.equal($('flashcard-detail').textContent, '');
  assert.equal($('word-accuracy').textContent, 'No reviews yet');
  assert.equal($('word-audio').disabled, true); // Missing voice doesn't block studying.
  assert.equal($('review-ratings').hidden, true);
  assert.equal($('start-reviews').disabled, false);
  await $('rating-buttons').children[4].onclick();
  assert.equal(submissions.length, 0); // Browsing must never affect scheduling.
  $('flashcard').onclick();
  assert.match($('flashcard-detail').textContent, /náam/);
  assert.equal($('flashcard-example').textContent, 'ขอน้ำครับ');
  $('flashcard').onclick();
  assert.equal($('flashcard-example').textContent, '');
  await $('start-reviews').onclick();
  assert.equal($('review-ratings').hidden, false);
  assert.equal($('rating-buttons').children[4].disabled, true);
  await $('rating-buttons').children[4].onclick();
  assert.equal(submissions.length, 0); // Reveal before rating.
  $('flashcard').onclick();
  assert.equal($('rating-buttons').children[4].disabled, false);
  await $('rating-buttons').children[4].onclick();
  assert.match($('session-status').textContent, /Network disconnected/);
  assert.equal($('rating-buttons').children[3].disabled, true); // Retry the identical answer after uncertain delivery.
  await $('rating-buttons').children[4].onclick();
  assert.equal(submissions.length, 2);
  assert.deepEqual(submissions[0], submissions[1]);
  assert.equal(reviews, 1);
  assert.equal($('flashcard-word').textContent, 'Review session complete');
  assert.equal($('card-count').textContent, '1 / 1 reviewed');
  assert.equal($('start-reviews').disabled, true);
  assert.equal($('word-due').textContent, 0);
  assert.equal($('word-accuracy').textContent, '100% (1/1)');
  assert.equal(progressRefreshes, 1);
  $('browse-words').onclick();
  assert.equal($('flashcard-word').textContent, 'น้ำ');
  assert.equal($('review-ratings').hidden, true);
  context.cards = [{category: 'Food', due_on: '2026-11-13'}, {category: 'Food', due_on: '2026-11-14'}, {category: 'Greetings', due_on: '2026-11-12'}];
  assert.equal(vm.runInContext("vocabularySessionCards(cards, 'Food', true, '2026-11-13').length", context), 1);
  assert.equal(vm.runInContext("vocabularySessionCards(cards, '', false, '2026-11-13').length", context), 3);
  assert.equal(vm.runInContext("vocabularySessionCards(cards, 'Shopping', true, '2026-11-13').length", context), 0);
  console.log('Vocabulary UI checks passed: flip, examples, no-audio fallback, due sessions, reveal-before-rating, failed-save retry, completion, statistics, and category filters.');
}
module.exports = runTests();
if (require.main === module) module.exports.catch((error) => { console.error(error); process.exitCode = 1; });
