const chatWindow = document.getElementById('chatWindow');
const chatForm = document.getElementById('chatForm');
const questionInput = document.getElementById('questionInput');
const suggestionButtons = document.querySelectorAll('.suggestion-card');

function addMessage(role, text, source = null) {
  const message = document.createElement('div');
  message.className = `message ${role}`;
  const label = role === 'user' ? 'You' : 'Assistant';
  message.innerHTML = `<div class="bubble-label">${label}</div><div>${text}</div>`;
  if (source) {
    const sourceLine = document.createElement('div');
    sourceLine.className = 'source';
    sourceLine.textContent = `Source: ${source}`;
    message.appendChild(sourceLine);
  }
  chatWindow.appendChild(message);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showLoading() {
  const loading = document.createElement('div');
  loading.className = 'message assistant loading';
  loading.textContent = 'Thinking...';
  chatWindow.appendChild(loading);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeLoading() {
  const loading = chatWindow.querySelector('.loading');
  if (loading) loading.remove();
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  addMessage('user', question);
  questionInput.value = '';
  showLoading();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await response.json();
    removeLoading();
    addMessage('assistant', data.answer, data.source);
  } catch (error) {
    removeLoading();
    addMessage('assistant', 'Sorry, something went wrong. Please try again.');
  }
});

suggestionButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const question = button.getAttribute('data-question');
    questionInput.value = question;
    questionInput.focus();
  });
});
