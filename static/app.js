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
let conversationHistory = [];
let conversationSources = [];
function saveConversation() {
  try {
    sessionStorage.setItem(TUTOR_SESSION_KEY, JSON.stringify({
      messages: conversationHistory,
      sources: conversationSources,
      level: $('tutor-level').value,
      mode: $('tutor-mode').value,
      pronunciation: $('tutor-pronunciation').checked
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
    conversationHistory = saved.messages;
    conversationSources = Array.isArray(saved.sources) ? saved.sources : [];
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
  const userMessage = appendMessage('user', text);
  $('user-input').value = '';
  const pendingHistory = [...conversationHistory, { role: 'user', content: text }];
  const pending = appendMessage('assistant', 'Your tutor is thinking…');
  status('chat-status', 'Waiting for your local Ollama tutor…');
  try {
    const data = await api('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: pendingHistory, use_web_search: $('web-search-toggle').checked, tutor: { level: $('tutor-level').value, mode: $('tutor-mode').value, pronunciation: $('tutor-pronunciation').checked } }) });
    pending.remove();
    appendMessage('assistant', data.response, data.doc_sources || [], data.web_sources || []);
    conversationHistory = [...pendingHistory, { role: 'assistant', content: data.response }];
    conversationSources.push({}, { docs: data.doc_sources || [], web: data.web_sources || [] });
    saveConversation();
    status('chat-status', (data.warnings || []).join(' '));
  } catch (error) {
    pending.remove();
    userMessage.remove();
    status('chat-status', `${error.message} Check that Flask and Ollama are running, then send again.`, 'error');
    if (!$('user-input').value) $('user-input').value = text;
  } finally {
    chatBusy = false;
    $('send-btn').disabled = false;
    $('clear-chat').disabled = false;
  }
});
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
  appendMessage('assistant', 'Sawasdee! What would you like to practice today?');
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
