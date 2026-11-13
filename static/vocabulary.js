'use strict';
// Session state is separate from persisted SM-2 state; only a rated due card changes its schedule.
function vocabularySessionCards(words, category, dueOnly, day) {
  return words.filter((word) => (!category || word.category === category) && (!dueOnly || word.due_on <= day));
}
(() => {
  let words = [];
  let day = '';
  let queue = [];
  let position = 0;
  let flipped = false;
  let reviewing = false;
  let reviewed = 0;
  let sessionTotal = 0;
  let saving = false;
  let pendingReview = null;
  let loadVersion = 0;
  let historyVersion = 0;
  const audio = new ThaiSpeechAudio(window);
  const ratings = ['0 · Forgot completely', '1 · Wrong; familiar answer', '2 · Wrong; answer seemed easy', '3 · Correct; difficult', '4 · Correct; hesitated', '5 · Correct; effortless'];
  function current() { return queue[position]; }
  function dueCards() { return vocabularySessionCards(words, $('vocabulary-category').value, true, day); }
  function voiceAvailable() { return audio.voices().length > 0 && !!window.SpeechSynthesisUtterance; }
  function refreshAudio() {
    const enabled = !!current() && voiceAvailable();
    $('word-audio').disabled = !enabled;
    $('example-audio').disabled = !enabled;
    status('vocabulary-audio-status', voiceAvailable() ? 'Browser Thai TTS; voice quality varies by device.' : 'No Thai speech voice available. Install a Thai device voice to enable audio. Cards and reviews still work.');
  }
  function renderCard() {
    historyVersion++;
    $('word-review-history').replaceChildren();
    const card = current();
    $('flashcard').disabled = !card || saving;
    $('review-ratings').hidden = !reviewing || !card;
    $('session-title').textContent = reviewing ? 'Recall, reveal, then rate' : 'Flip. Learn. Repeat.';
    $('card-count').textContent = reviewing ? `${reviewed} / ${sessionTotal} reviewed` : card ? `${position + 1} / ${queue.length}` : '0 words';
    $('flashcard-word').textContent = card ? card.thai : reviewing ? 'Review session complete' : 'No saved words in this category';
    $('flashcard-detail').textContent = card && flipped ? `${card.roman} · ${card.english}` : '';
    for (const field of ['thai', 'roman', 'english']) $('flashcard-example' + (field === 'thai' ? '' : '-' + field)).textContent = card && flipped ? card['example_' + field] : '';
    $('flip-hint').textContent = card ? flipped ? 'Click to hide the answer' : 'Recall the meaning, then click to reveal' : reviewing ? 'Your review dates are saved. Return when more words are due.' : 'Save lesson words or add a personal word to begin.';
    $('flashcard').setAttribute('aria-pressed', String(flipped));
    $('previous-card').disabled = saving || reviewing || position <= 0;
    $('next-card').disabled = saving || reviewing || position >= queue.length - 1 || !card;
    $('vocabulary-category').disabled = saving;
    $('browse-words').disabled = saving;
    $('start-reviews').disabled = saving || !dueCards().length;
    $('show-word-history').disabled = !card || saving;
    $('card-schedule').textContent = card ? `${card.category} · Due ${card.due_on} (Bangkok) · interval ${card.interval_days} day(s) · ${card.repetitions} successful repetition(s). ${card.lesson_id ? 'Saved from a lesson.' : 'Personal entry.'}` : '';
    document.querySelectorAll('[data-review-quality]').forEach((button) => {
      button.disabled = !card || !flipped || saving || (!!pendingReview && pendingReview.quality !== Number(button.dataset.reviewQuality));
    });
    refreshAudio();
  }
  function browse() {
    audio.cancel();
    reviewing = false; position = 0; flipped = false; pendingReview = null;
    queue = vocabularySessionCards(words, $('vocabulary-category').value, false, day);
    status('session-status', 'Browsing does not change review dates. Start a due review session to record recall.');
    renderCard();
  }
  function renderCollection() {
    $('vocabulary-list').replaceChildren();
    const visible = vocabularySessionCards(words, $('vocabulary-category').value, false, day);
    if (!visible.length) $('vocabulary-list').append(element('p', 'No saved words here yet. Import lesson vocabulary or add a personal word.', 'empty'));
    visible.forEach((word) => {
      const row = element('div', '', 'vocab-row');
      const button = element('button', word.thai, 'word-select');
      button.lang = 'th'; button.type = 'button';
      button.onclick = () => {
        if (saving) return;
        browse(); position = queue.findIndex((item) => item.id === word.id); renderCard();
      };
      const details = element('span', word.english);
      details.append(element('small', word.roman), element('small', `${word.category} · due ${word.due_on}`));
      row.append(button, details); $('vocabulary-list').append(row);
    });
  }
  async function loadWords(keepSession = false) {
    const version = ++loadVersion;
    const result = await api('/api/vocabulary');
    if (version !== loadVersion) return;
    words = result.words; day = result.today;
    $('word-total').textContent = result.stats.total;
    $('word-due').textContent = result.stats.due;
    $('word-mastered').textContent = result.stats.mastered;
    $('word-accuracy').textContent = result.stats.accuracy === null ? 'No reviews yet' : `${result.stats.accuracy}% (${result.stats.recalled}/${result.stats.reviews})`;
    renderCollection();
    if (!keepSession) browse(); else renderCard();
  }
  async function startReview() {
    if (saving) return;
    try {
      await loadWords();
      reviewing = true; reviewed = 0; position = 0; flipped = false;
      queue = dueCards(); sessionTotal = queue.length; pendingReview = null;
      status('session-status', queue.length ? 'Review only due words in the selected category. Reveal each answer before rating.' : 'No reviews due in this category. Browse or add words instead.');
      renderCard();
    } catch (error) { status('vocabulary-status', error.message, 'error'); }
  }
  async function rateCard(quality) {
    const card = current();
    if (!reviewing || !card || !flipped || saving) return;
    if (pendingReview && pendingReview.quality !== quality) return;
    pendingReview ||= {quality, revision: card.revision, attempt_id: crypto.randomUUID ? crypto.randomUUID() : '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (digit) => (digit ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> digit / 4).toString(16))};
    saving = true; renderCard();
    status('session-status', 'Saving review…');
    try {
      const result = await api(`/api/vocabulary/${card.id}/review`, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(pendingReview)});
      audio.cancel();
      queue.shift(); position = 0; reviewed++; flipped = false; pendingReview = null;
      status('session-status', `Saved. Next review: ${result.review.due_on} · ${result.review.interval_days} day(s).`);
      try { await loadWords(true); await refreshProgress(); }
      catch { status('vocabulary-status', 'Review saved. Refresh to update statistics.', 'error'); }
    } catch (error) {
      status('session-status', `${error.message} Retry the same rating, or refresh vocabulary to load the saved state.`, 'error');
    } finally { saving = false; renderCard(); }
  }
  ratings.forEach((label, quality) => {
    const button = element('button', label, 'button secondary');
    button.type = 'button'; button.dataset.reviewQuality = quality;
    button.disabled = true; button.onclick = () => rateCard(quality);
    $('rating-buttons').append(button);
  });
  $('flashcard').onclick = () => { if (current() && !saving) { flipped = !flipped; renderCard(); } };
  $('previous-card').onclick = () => { if (!saving && !reviewing && position > 0) { position--; flipped = false; audio.cancel(); renderCard(); } };
  $('next-card').onclick = () => { if (!saving && !reviewing && position + 1 < queue.length) { position++; flipped = false; audio.cancel(); renderCard(); } };
  $('start-reviews').onclick = startReview;
  $('browse-words').onclick = () => { if (!saving) browse(); };
  $('vocabulary-category').onchange = () => { if (!saving) { browse(); renderCollection(); } };
  $('reload-vocabulary').onclick = async () => {
    if (saving) return;
    try { await loadWords(); await refreshProgress(); status('vocabulary-status', 'Vocabulary refreshed.'); }
    catch (error) { status('vocabulary-status', error.message, 'error'); }
  };
  async function play(text) {
    if (!text) return;
    status('vocabulary-audio-status', 'Playing browser-generated Thai audio…');
    try {
      const played = await audio.play(text, audio.voices()[0]?.voiceURI, 0.8);
      if (played) status('vocabulary-audio-status', 'Playback finished.');
    } catch (error) { status('vocabulary-audio-status', error.message, 'error'); }
  }
  $('word-audio').onclick = () => play(current()?.thai);
  $('example-audio').onclick = () => play(current()?.example_thai);
  window.speechSynthesis?.addEventListener('voiceschanged', refreshAudio);
  $('show-word-history').onclick = async () => {
    const card = current();
    if (!card) return;
    const version = ++historyVersion;
    try {
      const result = await api(`/api/vocabulary/${card.id}/history`);
      if (version !== historyVersion) return;
      $('word-review-history').replaceChildren();
      if (!result.history.length) $('word-review-history').append(element('li', 'No reviews yet.'));
      result.history.forEach((review) => $('word-review-history').append(element('li', `${new Date(review.reviewed_at).toLocaleString()} · rating ${review.quality}/5 · next due ${review.due_on} · interval ${review.interval_days} days`)));
    } catch (error) { status('vocabulary-status', error.message, 'error'); }
  };
  async function saveWords(form, body) {
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
      const result = await api('/api/vocabulary', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
      status('vocabulary-status', `${result.added} new word(s) saved. Existing words and schedules are kept.`, 'success');
      if (form.id === 'add-word-form') form.reset();
      try { await loadWords(reviewing); await refreshProgress(); }
      catch { status('vocabulary-status', 'Words saved. Refresh vocabulary to update the collection.', 'error'); }
    } catch (error) { status('vocabulary-status', error.message, 'error'); }
    finally { button.disabled = false; }
  }
  $('add-word-form').addEventListener('submit', (event) => {
    event.preventDefault(); saveWords(event.currentTarget, Object.fromEntries(new FormData(event.currentTarget)));
  });
  $('import-lesson-form').addEventListener('submit', (event) => {
    event.preventDefault(); saveWords(event.currentTarget, {lesson_id: $('vocabulary-lesson').value});
  });
  window.addEventListener('vocabularychanged', () => loadWords(reviewing).catch((error) => status('vocabulary-status', error.message, 'error')));
  window.addEventListener('hashchange', () => {
    if (!location.hash.startsWith('#vocabulary')) { audio.cancel(); return; }
    if (location.hash === '#vocabulary/review') startReview();
    else if (!saving) loadWords().catch((error) => status('vocabulary-status', error.message, 'error'));
  });
  window.addEventListener('pagehide', () => audio.cancel());
  document.addEventListener('visibilitychange', () => { if (document.hidden) audio.cancel(); });
  async function initialize() {
    try {
      const content = await api('/api/vocabulary/catalog');
      for (const category of content.categories) {
        for (const id of ['vocabulary-category', 'manual-word-category']) {
          const option = element('option', category); option.value = category; $(id).append(option);
        }
      }
      for (const lesson of content.lessons) {
        const option = element('option', lesson.title); option.value = lesson.id; $('vocabulary-lesson').append(option);
      }
      await loadWords();
      if (location.hash === '#vocabulary/review') await startReview();
    } catch (error) { status('vocabulary-status', `${error.message} Refresh the page to retry.`, 'error'); }
  }
  refreshAudio(); initialize();
})();
