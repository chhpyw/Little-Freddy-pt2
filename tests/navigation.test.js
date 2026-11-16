// Run with Node.js: node tests/navigation.test.js. No packages required.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/app.js'), 'utf8');
const navigation = source.slice(0, source.indexOf("window.addEventListener('hashchange', navigate)"));
const sections = ['dashboard', 'tutor', 'learn', 'vocabulary', 'library', 'speaking'].map((id) => ({ id, hidden: false }));
const links = sections.map(({ id }) => ({
  dataset: { nav: id }, classList: { toggle() {} },
  setAttribute(name, value) { this[name] = value; },
  removeAttribute(name) { delete this[name]; }
}));
const breadcrumb = {};
let libraryLoads = 0;
const context = vm.createContext({
  location: { hash: '' },
  loadFiles() { libraryLoads++; },
  document: {
    title: '',
    getElementById() { return breadcrumb; },
    querySelector() { return { textContent: 'Page title' }; },
    querySelectorAll(selector) { return selector === '.page' ? sections : links; }
  }
});
vm.runInContext(navigation, context);
for (const [hash, expected] of [
  ['', 'dashboard'], ['#tutor', 'tutor'], ['#learn', 'learn'],
  ['#learn/greetings', 'learn'], ['#learn/shopping', 'learn'],
  ['#vocabulary/review', 'vocabulary'], ['#speaking/food/listening', 'speaking'], ['#speaking', 'speaking'], ['#vocabulary', 'vocabulary'], ['#library', 'library'], ['#unknown', 'dashboard']
]) {
  context.location.hash = hash;
  vm.runInContext('navigate()', context);
  assert.deepEqual(sections.filter((section) => !section.hidden).map((section) => section.id), [expected]);
  assert.equal(links.find((link) => link['aria-current'] === 'page').dataset.nav, expected);
  assert.ok(breadcrumb.textContent);
}
assert.equal(libraryLoads, 1);
console.log('11 navigation cases passed, including lesson deep links and fallback.');
