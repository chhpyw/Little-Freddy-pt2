'use strict';
let curriculumData;
let progressData;
let activeLesson;
let lessonHistory = [];
let lessonRequest = 0;
let lessonChatBusy = false;
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function updateTranslations() {
  document.querySelectorAll('#lesson-content .translation').forEach((node) => {
    node.hidden = !$('translation-toggle').checked;
  });
}
$('translation-toggle').addEventListener('change', updateTranslations);
function speak(thai) {
  if (!('speechSynthesis' in window)) return;
  const voice = speechSynthesis.getVoices().find((item) => item.lang.toLowerCase().startsWith('th'));
  if (!voice) {
    status('speech-status', 'No Thai voice is installed. Add a Thai voice in your device speech settings, then try again.');
    return;
  }
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(thai);
  utterance.lang = 'th-TH';
  utterance.voice = voice;
  utterance.rate = 0.8;
  utterance.onerror = () => status('speech-status', 'Speech playback failed. Try again or check your device voice settings.', 'error');
  speechSynthesis.speak(utterance);
  status('speech-status', 'Playing Thai audio. Listen, then repeat.');
}
function phraseRow(thai, roman, english) {
  const row = element('div', '', 'phrase-row');
  const script = element('strong', thai);
  script.lang = 'th';
  const details = element('div');
  details.append(script, element('p', roman, 'romanization'), element('p', english, 'translation'));
  const play = element('button', 'Listen', 'button secondary');
  play.type = 'button';
  play.disabled = !('speechSynthesis' in window);
  play.setAttribute('aria-label', `Listen to ${thai}`);
  play.onclick = () => speak(thai);
  row.append(details, play);
  return row;
}
async function refreshProgress() {
  progressData = await api('/api/progress');
  $('completed-count').textContent = `${progressData.completed} / ${progressData.total}`;
  $('average-score').textContent = progressData.attempts ? `${progressData.average_score}%` : 'No quizzes yet';
  $('attempt-count').textContent = progressData.attempts;
  $('real-progress').value = progressData.percent;
  $('speech-completed').textContent = `${progressData.speech.completed} / ${progressData.speech.total}`;
  $('speech-attempts').textContent = `${progressData.speech.attempts} saved listening / speaking attempts`;
  $('speech-progress').value = progressData.speech.completed;
  $('speech-progress').max = progressData.speech.total;
  const stats = progressData.vocabulary;
  $('dashboard-word-total').textContent = stats.total;
  $('dashboard-word-due').textContent = stats.due;
  $('dashboard-word-mastered').textContent = stats.mastered;
  $('dashboard-word-accuracy').textContent = stats.accuracy === null ? 'No reviews yet' : `${stats.accuracy}%`;
  $('recommendations').replaceChildren();
  progressData.recommendations.forEach((item) => {
    const link = element('a', '', 'recommendation');
    link.href = item.href;
    link.append(element('h3', item.title), element('p', item.reason));
    $('recommendations').append(link);
  });
  status('progress-status', '');
  renderCourses();
}
function renderCourses() {
  if (!curriculumData || !progressData) return;
  $('course-grid').replaceChildren();
  curriculumData.courses.forEach((course) => {
    const card = element('article', '', 'card course');
    card.append(element('h2', `${course.level} · ${course.title}`));
    const goals = element('ul');
    course.goals.forEach((goal) => goals.append(element('li', goal)));
    card.append(goals);
    const lessons = curriculumData.lessons.filter((lesson) => lesson.level === course.level);
    if (!lessons.length) card.append(element('p', 'Curriculum roadmap · guided units planned. Continue practicing these goals with your AI tutor.'));
    lessons.forEach((lesson, index) => {
      const saved = progressData.lessons.find((row) => row.lesson_id === lesson.id);
      const link = element('a', `${index + 1}. ${lesson.title}`, 'lesson-link');
      link.href = `#learn/${lesson.id}`;
      link.append(element('small', saved ? `${saved.completed ? 'Completed' : 'In progress'} · best ${saved.best_score}% · ${saved.attempts} attempt(s)` : 'Not started'));
      card.append(link);
    });
    if (!lessons.length) {
      const practice = element('button', `Practice ${course.level} goals with AI ↗`, 'button secondary');
      practice.onclick = () => {
        $('tutor-level').value = course.level === 'A2' ? 'Beginner' : course.level === 'B1' ? 'Intermediate' : 'Advanced';
        $('tutor-mode').value = 'Guided Lesson';
        $('tutor-level').dispatchEvent(new Event('change'));
        $('user-input').value = `Guide me through ${course.level} Thai practice: ${course.goals.join('; ')}. Begin with one manageable task.`;
        location.hash = 'tutor';
        $('user-input').focus();
      };
      card.append(practice);
    }
    $('course-grid').append(card);
  });
}
async function openLesson() {
  const version = ++lessonRequest;
  const match = location.hash.match(/^#learn\/([^/]+)$/);
  $('lesson-preview').hidden = true;
  activeLesson = null;
  if (!match) return;
  status('learning-status', 'Loading lesson…');
  try {
    const lesson = await api(`/api/lessons/${encodeURIComponent(match[1])}`);
    if (version !== lessonRequest) return;
    activeLesson = lesson;
    lessonHistory = [];
    $('lesson-chat').replaceChildren();
    $('lesson-message').value = '';
    status('lesson-chat-status', '');
    status('quiz-result', '');
    $('lesson-title').textContent = `${lesson.level} · ${lesson.title}`;
    const content = $('lesson-content');
    content.replaceChildren(element('h3', 'Learning objectives'));
    const objectives = element('ul');
    lesson.objectives.forEach((goal) => objectives.append(element('li', goal)));
    content.append(objectives, element('h3', 'Listen and understand'));
    const saveAll = element('button', 'Save all lesson words', 'button secondary');
    saveAll.type = 'button';
    const saveStatus = element('p', '', 'status');
    saveStatus.setAttribute('role', 'status');
    async function saveWords(button, wordIndex) {
      button.disabled = true;
      try {
        const result = await api('/api/vocabulary', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({lesson_id: lesson.id, ...(wordIndex === undefined ? {} : {word_index: wordIndex})})});
        saveStatus.textContent = `${result.added} new word(s) saved. Existing words and schedules are kept.`;
        await refreshProgress();
        window.dispatchEvent(new Event('vocabularychanged'));
      } catch (error) { saveStatus.textContent = error.message; }
      finally { button.disabled = false; }
    }
    saveAll.onclick = () => saveWords(saveAll);
    content.append(saveAll, saveStatus);
    lesson.vocabulary.forEach((word, index) => {
      const row = phraseRow(word.thai, word.roman, word.english);
      const button = element('button', 'Save word', 'button secondary');
      button.type = 'button'; button.setAttribute('aria-label', `Save ${word.thai}`);
      button.onclick = () => saveWords(button, index);
      row.append(button);
      content.append(row);
    });
    content.append(element('h3', 'A real conversation'));
    lesson.dialogue.forEach((line) => content.append(phraseRow(line.thai, line.roman, line.english)));
    content.append(element('h3', 'Build a sentence'), element('p', lesson.pattern),
      element('h3', 'Politeness and tone'),
      element('p', 'ครับ (khráp) is commonly used by men. Women commonly use ค่ะ (khâ) for statements and คะ (khá) for questions. Choose particles that fit your identity and speaking style. Add them at the end of a sentence.'),
      element('p', 'Thai has five tones. Pitch and vowel length can change meaning. Romanization uses à (low), â (falling), á (high), ǎ (rising), and unmarked vowels (mid). Listen to a Thai voice and repeat; playback does not assess your pronunciation.'));
    curriculumData.tones.forEach(([tone, thai, roman, english, hint]) => {
      content.append(element('p', `${tone}: ${hint}`), phraseRow(thai, roman, english));
    });
    $('quiz-questions').replaceChildren();
    lesson.questions.forEach((question, index) => {
      const fieldset = element('fieldset');
      fieldset.append(element('legend', `${index + 1}. ${question.prompt}`));
      if (question.type === 'choice') {
        question.options.forEach((option) => {
          const label = element('label');
          const input = element('input');
          input.type = 'radio'; input.name = `question-${index}`; input.value = option; input.required = true;
          label.append(input, document.createTextNode(` ${option}`));
          fieldset.append(label);
        });
      } else {
        const input = element('input');
        input.type = 'text'; input.name = `question-${index}`; input.required = true; input.maxLength = 300;
        input.setAttribute('aria-label', question.prompt);
        input.autocomplete = 'off';
        fieldset.append(input);
      }
      const feedback = element('p', '', 'status');
      feedback.id = `feedback-${index}`;
      fieldset.append(feedback);
      $('quiz-questions').append(fieldset);
    });
    $('lesson-scenario').textContent = lesson.scenario;
    updateTranslations();
    status('speech-status', 'speechSynthesis' in window ? 'Listen uses a Thai voice installed on your device, when available.' : 'Your browser does not support speech playback. Use the pronunciation guides.');
    $('lesson-preview').hidden = false;
    status('learning-status', '');
    $('lesson-title').focus();
  } catch (error) { if (version === lessonRequest) status('learning-status', error.message, 'error'); }
}
$('lesson-quiz').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!activeLesson) return;
  const lesson = activeLesson;
  const version = lessonRequest;
  const form = new FormData(event.currentTarget);
  const button = event.currentTarget.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const result = await api(`/api/lessons/${lesson.id}/submit`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ answers: lesson.questions.map((_, index) => form.get(`question-${index}`)) }) });
    if (version === lessonRequest) {
      result.feedback.forEach((feedback, index) => status(`feedback-${index}`, feedback.correct ? 'Correct!' : `Try again. Answer: ${feedback.answer}`, feedback.correct ? 'success' : 'error'));
      status('quiz-result', `${result.score}% · ${result.passed ? 'Lesson completed!' : 'Keep practicing; 75% completes the lesson.'} Progress saved. Best scores are kept.`, result.passed ? 'success' : '');
    }
    await refreshProgress();
  } catch (error) { if (version === lessonRequest) status('quiz-result', error.message, 'error'); }
  finally { button.disabled = false; }
});
$('lesson-chat-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = $('lesson-message').value.trim();
  if (!activeLesson || !text || lessonChatBusy) return;
  const version = lessonRequest;
  const history = [...lessonHistory, { role: 'user', content: text }];
  const button = event.currentTarget.querySelector('button');
  lessonChatBusy = true; button.disabled = true;
  status('lesson-chat-status', 'Waiting for Ollama…');
  try {
    const result = await api('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: history, lesson_id: activeLesson.id, translations: $('translation-toggle').checked, tutor: { level: 'Beginner', mode: 'Roleplay', pronunciation: true } }) });
    if (version !== lessonRequest) return;
    $('lesson-chat').append(element('div', text, 'message user-message'), element('div', result.response, 'message assistant-message'));
    $('lesson-chat').scrollTop = $('lesson-chat').scrollHeight;
    lessonHistory = [...history, { role: 'assistant', content: result.response }];
    $('lesson-message').value = '';
    status('lesson-chat-status', '');
  } catch (error) { if (version === lessonRequest) status('lesson-chat-status', `${error.message} Your message is kept; retry after starting Ollama.`, 'error'); }
  finally { lessonChatBusy = false; button.disabled = false; }
});
window.addEventListener('hashchange', () => {
  openLesson();
  if (location.hash === '#dashboard') refreshProgress().catch((error) => status('progress-status', error.message, 'error'));
});
async function initializeLearning() {
  try {
    curriculumData = await api('/api/curriculum');
    await refreshProgress();
    await openLesson();
  } catch (error) {
    status('learning-status', `${error.message} Reload to retry.`, 'error');
    status('progress-status', error.message, 'error');
  }
}
initializeLearning();
