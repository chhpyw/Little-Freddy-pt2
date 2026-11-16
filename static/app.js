'use strict';
const $ = (id) => document.getElementById(id);
const pageNames = { speaking: 'Speaking & Listening practice', dashboard: 'Your learning overview', tutor: 'Your AI practice partner', learn: 'Explore your learning path', vocabulary: 'Your vocabulary collection', library: 'Your document collection' };
function navigate() {
  const requested = location.hash.startsWith('#learn/') ? 'learn' : location.hash.startsWith('#vocabulary/') ? 'vocabulary' : location.hash.startsWith('#speaking/') ? 'speaking' : location.hash.slice(1) || 'dashboard';
  const page = Object.hasOwn(pageNames, requested) ? requested : 'dashboard';
  document.querySelectorAll('.page').forEach((section) => { section.hidden = section.id !== page; });
  document.querySelectorAll('[data-nav]').forEach((link) => {
    const active = link.dataset.nav === page;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  $('breadcrumb').textContent = pageNames[page];
  document.title = `${document.querySelector(`#${page} h1`).textContent} · Freddy Learns Thai`;
  if (page === 'library') loadFiles();
}
window.addEventListener('hashchange', navigate);
function status(id, text, type = '') {
  $(id).textContent = text;
  $(id).className = `status ${type}`;
}
async function api(url, options = {}) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); }
  catch { throw new Error(response.status === 413 ? 'This file exceeds the 50 MB upload limit.' : 'The server returned an unexpected response. Please try again.'); }
  if (!response.ok) throw new Error(data.error || 'The request failed. Please try again.');
  return data;
}
function sourceLink(label, url) {
  const link = document.createElement('a');
  link.textContent = label;
  link.href = url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  return link;
}
function appendMessage(role, text, docs = [], web = []) {
  const message = document.createElement('div');
  message.className = `message ${role}-message`;
  message.textContent = text;
  if (docs.length || web.length) {
    const sources = document.createElement('div');
    sources.className = 'sources';
    sources.textContent = 'Sources used';
    docs.forEach((name) => sources.append(sourceLink(name, `/uploads/${encodeURIComponent(name)}`)));
    web.forEach((url) => {
      try {
        const parsed = new URL(url);
        if (['http:', 'https:'].includes(parsed.protocol)) sources.append(sourceLink(url, parsed.href));
      } catch { /* Ignore malformed source URLs. */ }
    });
    message.append(sources);
  }
  $('chat-window').append(message);
  $('chat-window').scrollTop = $('chat-window').scrollHeight;
  return message;
}
const TUTOR_SESSION_KEY = 'freddy-thai-tutor-session';
const TUTOR_VALIDATION_VERSION = 'thai-fields-v1';
function teachingText(teaching, reviewed = []) {
  const foreign = /[\u1000-\u109f\uaa60-\uaa7f\ua9e0-\ua9ff\u{116d0}-\u{116ff}\u1780-\u17ff\u19e0-\u19ff]/u;
  const safe = (text, thaiOnly = false) => typeof text === 'string' && !foreign.test(text) && [...text].every((char) =>
    !/[\p{L}\p{M}]/u.test(char) || /\p{Script=Thai}/u.test(char) || (!thaiOnly && /[\p{Script=Latin}\u0300-\u036f]/u.test(char)));
  if (!teaching || !safe(teaching.explanation) || !Array.isArray(teaching.examples) || !teaching.examples.length ||
      !Array.isArray(teaching.language_notes) || !Array.isArray(teaching.reference_titles)) throw Error('Unvalidated tutor response was blocked. Please retry.');
  const lines = teaching.explanation ? [`AI-generated conversation (not language reviewed): ${teaching.explanation}`] : [];
  teaching.examples.forEach((example, index) => {
    if (!safe(example.thai, true) || !/[\u0e01-\u0e2e]/u.test(example.thai) || !safe(example.english) || !safe(example.romanization) || /\p{Script=Thai}/u.test(example.romanization)) throw Error('Invalid Thai teaching fields were blocked. Please retry.');
    const source = reviewed[index];
    if (source && (source.thai !== example.thai || (example.english && source.english !== example.english) ||
        (example.romanization && source.romanization !== example.romanization) || typeof source.lesson_id !== 'string')) throw Error('Curriculum source mismatch was blocked.');
    lines.push(source ? `Reviewed curriculum example (${source.lesson_id}; not native-verified): ${example.thai}` : `Generated Thai text (script checked; language unreviewed): ${example.thai}`);
    if (example.romanization) lines.push(`${source ? 'Curriculum pronunciation guide' : 'Generated pronunciation guide (unreviewed)'}: ${example.romanization}`);
    if (example.english) lines.push(`${source ? 'Curriculum meaning' : 'Generated meaning (unreviewed)'}: ${example.english}`);
    if (source && source.usage) lines.push(`Curriculum usage note: ${source.usage}`);
  });
  teaching.language_notes.forEach((note) => {
    if (typeof note.language !== 'string' || !/^[a-z -]+$/i.test(note.language) || typeof note.quote !== 'string' || !safe(note.explanation) ||
        (/thai/i.test(note.language) && (!safe(note.quote, true) || !/[\u0e01-\u0e2e]/u.test(note.quote)))) throw Error('Invalid language quotation was blocked.');
    lines.push(`Language quotation (${note.language}): ${note.quote}`, note.explanation);
  });
  teaching.reference_titles.forEach((title) => {
    if (typeof title !== 'string') throw Error('Invalid reference title.');
    lines.push(`Reference title: ${title}`);
  });
  return lines.join('\n');
}
let conversationHistory = [];
let conversationSources = [];
function saveConversation() {
  try {
    sessionStorage.setItem(TUTOR_SESSION_KEY, JSON.stringify({
      messages: conversationHistory,
      sources: conversationSources,
      level: $('tutor-level').value,
      mode: $('tutor-mode').value,
      pronunciation: $('tutor-pronunciation').checked,
      draft: $('user-input').value
    }));
  } catch { /* Chat remains usable if browser storage is unavailable. */ }
}
function restoreConversation() {
  try {
    const saved = JSON.parse(sessionStorage.getItem(TUTOR_SESSION_KEY));
    if (!saved || !Array.isArray(saved.messages) || !saved.messages.every((message) =>
      message && ['user', 'assistant'].includes(message.role) && typeof message.content === 'string')) return;
    if (['Beginner', 'Intermediate', 'Advanced'].includes(saved.level)) $('tutor-level').value = saved.level;
    if (['Free Chat', 'Guided Lesson', 'Roleplay', 'Grammar Help'].includes(saved.mode)) $('tutor-mode').value = saved.mode;
    if (typeof saved.pronunciation === 'boolean') $('tutor-pronunciation').checked = saved.pronunciation;
    if (typeof saved.draft === 'string' && saved.draft.length <= 20000) $('user-input').value = saved.draft;
    conversationHistory = [];
    conversationSources = [];
    saved.messages.forEach((message, index) => {
      if (message.role === 'assistant') {
        try {
          if (message.script_validation !== TUTOR_VALIDATION_VERSION) return;
          message = {...message, content: teachingText(message.teaching, message.reviewed_examples || [])};
        } catch { return; }
      }
      conversationHistory.push(message);
      conversationSources.push(Array.isArray(saved.sources) ? saved.sources[index] || {} : {});
    });
    if (conversationHistory.length) {
      $('chat-window').replaceChildren();
      conversationHistory.forEach((message, index) => {
        const sources = conversationSources[index] || {};
        const docs = Array.isArray(sources.docs) ? sources.docs.filter((name) => typeof name === 'string') : [];
        const web = Array.isArray(sources.web) ? sources.web.filter((url) => typeof url === 'string') : [];
        appendMessage(message.role, message.content, docs, web);
      });
    }
  } catch { /* Ignore unavailable storage or an invalid saved session. */ }
}
restoreConversation();
const levelHints = { Beginner: 'Short Thai sentences with English translations.', Intermediate: 'Mostly Thai with English help for unfamiliar words.', Advanced: 'Natural Thai; English explanations when needed or requested.' };
$('tutor-level-hint').textContent = `${levelHints[$('tutor-level').value]} Settings apply to your next reply.`;
let chatBusy = false;
$('chat-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = $('user-input').value.trim();
  if (!text || chatBusy) return;
  chatBusy = true;
  $('send-btn').disabled = true;
  $('clear-chat').disabled = true;
  saveConversation();
  const last = conversationHistory[conversationHistory.length - 1];
  const reusePending = last && last.role === 'user' && last.content === text;
  const userMessage = reusePending ? null : appendMessage('user', text);
  $('user-input').value = '';
  const pendingHistory = reusePending ? [...conversationHistory] : [...conversationHistory, { role: 'user', content: text }];
  const pendingSources = reusePending ? [...conversationSources] : [...conversationSources, {}];
  const pending = appendMessage('assistant', 'Your tutor is thinking…');
  status('chat-status', 'Waiting for your local Ollama tutor…');
  try {
    const data = await api('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: pendingHistory, use_web_search: $('web-search-toggle').checked, tutor: { level: $('tutor-level').value, mode: $('tutor-mode').value, pronunciation: $('tutor-pronunciation').checked } }) });
    if (data.script_validation !== TUTOR_VALIDATION_VERSION) throw Error('The Flask server is using an older tutor response format. Restart Flask and refresh this page.');
    const reply = teachingText(data.teaching, data.reviewed_examples || []);
    const fallback = data.response_kind === 'reviewed_fallback';
    if (fallback && (data.ai_commentary_accepted !== false || !Array.isArray(data.reviewed_examples) ||
        data.reviewed_examples.length !== data.teaching.examples.length)) throw Error('An unvalidated lesson fallback was blocked.');
    pending.remove();
    appendMessage('assistant', fallback ? `Reviewed lesson fallback — AI commentary was not accepted.\n${reply}` : reply, data.doc_sources || [], data.web_sources || []);
    if (fallback) {
      conversationHistory = pendingHistory; // Learner context only; no rejected AI reply.
      conversationSources = pendingSources;
      if (!$('user-input').value) $('user-input').value = text;
      saveConversation();
      status('chat-status', (data.warnings || []).join(' ') || 'Showing reviewed lesson examples only. Your draft is kept.');
      return;
    }
    conversationHistory = [...pendingHistory, { role: 'assistant', content: reply, teaching: data.teaching, reviewed_examples: data.reviewed_examples || [], script_validation: data.script_validation }];
    conversationSources = [...pendingSources, { docs: data.doc_sources || [], web: data.web_sources || [] }];
    saveConversation();
    status('chat-status', (data.warnings || []).join(' '));
  } catch (error) {
    pending.remove();
    if (userMessage) userMessage.remove();
    status('chat-status', `${error.message} Your draft was kept; retry when ready.`, 'error');
    if (!$('user-input').value) $('user-input').value = text;
    saveConversation();
  } finally {
    chatBusy = false;
    $('send-btn').disabled = false;
    $('clear-chat').disabled = false;
  }
});
$('user-input').addEventListener('input', saveConversation);
$('user-input').addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    $('chat-form').requestSubmit();
  }
});
$('clear-chat').addEventListener('click', () => {
  conversationHistory = [];
  conversationSources = [];
  saveConversation();
  $('chat-window').replaceChildren();
  $('user-input').value = '';
  appendMessage('assistant', 'สวัสดี! (sà wàt dii — Hello!) What would you like to practice today?');
  status('chat-status', '');
});
$('tutor-level').addEventListener('change', () => {
  const hints = { Beginner: 'Short Thai sentences with English translations.', Intermediate: 'Mostly Thai with English help for unfamiliar words.', Advanced: 'Natural Thai; English explanations when needed or requested.' };
  $('tutor-level-hint').textContent = `${hints[$('tutor-level').value]} Settings apply to your next reply.`;
  $('tutor-pronunciation').checked = $('tutor-level').value === 'Beginner';
});
['tutor-level', 'tutor-mode', 'tutor-pronunciation'].forEach((id) => {
  $(id).addEventListener('change', saveConversation);
});
document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => {
  $('user-input').value = button.dataset.prompt;
  $('user-input').focus();
}));
let filesRequest = 0;
async function loadFiles() {
  const currentRequest = ++filesRequest;
  try {
    const files = await api('/files');
    if (currentRequest !== filesRequest) return;
    $('files-list').replaceChildren();
    $('file-count').textContent = `(${files.length})`;
    if (!files.length) {
      const empty = document.createElement('li');
      empty.className = 'empty';
      empty.textContent = 'Your library is ready for its first document. Upload a PDF to get started.';
      $('files-list').append(empty);
    }
    files.forEach((file) => {
      const row = document.createElement('li');
      row.className = 'file-item';
      const icon = document.createElement('span');
      icon.className = 'stat-icon orange';
      icon.textContent = '▱';
      const info = document.createElement('div');
      info.className = 'file-info';
      const link = sourceLink(file.name, `/uploads/${encodeURIComponent(file.name)}`);
      const size = document.createElement('small');
      size.textContent = `${file.size} · View document ↗`;
      info.append(link, size);
      const remove = document.createElement('button');
      remove.className = 'button delete-btn';
      remove.textContent = 'Delete';
      remove.setAttribute('aria-label', `Delete ${file.name}`);
      remove.addEventListener('click', async () => {
        if (!window.confirm(`Delete ${file.name} and its retrieval index?`)) return;
        remove.disabled = true;
        try {
          const result = await api(`/files/${encodeURIComponent(file.name)}`, { method: 'DELETE' });
          status('upload-status', result.message, 'success');
          await loadFiles();
        } catch (error) { status('upload-status', error.message, 'error'); }
        finally { remove.disabled = false; }
      });
      row.append(icon, info, remove);
      $('files-list').append(row);
    });
  } catch (error) { status('upload-status', `Could not load your library: ${error.message}`, 'error'); }
}
$('refresh-files').addEventListener('click', loadFiles);
$('upload-btn').addEventListener('click', () => $('file-upload').click());
$('file-upload').addEventListener('change', async () => {
  const file = $('file-upload').files[0];
  if (!file) return;
  if (file.size > 50 * 1024 * 1024) { status('upload-status', 'Please choose a file smaller than 50 MB.', 'error'); $('file-upload').value = ''; return; }
  if (!/\.(pdf|txt|docx|md)$/i.test(file.name)) { status('upload-status', 'Please choose a PDF, TXT, DOCX, or Markdown file.', 'error'); $('file-upload').value = ''; return; }
  const form = new FormData();
  form.append('file', file);
  $('upload-btn').disabled = true;
  status('upload-status', 'Uploading and indexing… Longer documents can take several minutes.');
  try {
    const result = await api('/upload', { method: 'POST', body: form });
    status('upload-status', result.message, 'success');
  } catch (error) { status('upload-status', error.message, 'error'); }
  finally {
    $('upload-btn').disabled = false;
    $('file-upload').value = '';
    await loadFiles();
  }
});
navigate();
