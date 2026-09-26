const form = document.getElementById('chat-form');
const input = document.getElementById('question');
const sendButton = document.getElementById('send-button');
const messages = document.getElementById('messages');
const welcomeCard = document.getElementById('welcome-card');
const conversation = document.getElementById('conversation');
const newChatButton = document.getElementById('new-chat');
const serviceStatus = document.getElementById('service-status');
const statusText = document.getElementById('status-text');

function scrollToLatest() {
  conversation.scrollTop = conversation.scrollHeight;
}

function appendInlineMarkdown(parent, text) {
  const tokenPattern = /(`[^`]+`|\*\*[^*]+\*\*)/g;
  let cursor = 0;
  for (const match of text.matchAll(tokenPattern)) {
    parent.append(document.createTextNode(text.slice(cursor, match.index)));
    const token = match[0];
    const element = document.createElement(token.startsWith('`') ? 'code' : 'strong');
    element.textContent = token.startsWith('`') ? token.slice(1, -1) : token.slice(2, -2);
    parent.append(element);
    cursor = match.index + token.length;
  }
  parent.append(document.createTextNode(text.slice(cursor)));
}

function renderMarkdown(container, markdown) {
  const lines = String(markdown).replace(/\r\n?/g, '\n').split('\n');
  let paragraph = [];
  let list = null;

  const closeList = () => {
    if (list) container.append(list);
    list = null;
  };
  const flushParagraph = () => {
    if (!paragraph.length) return;
    const p = document.createElement('p');
    p.className = 'message-copy';
    appendInlineMarkdown(p, paragraph.join(' '));
    container.append(p);
    paragraph = [];
  };

  for (let index = 0; index < lines.length;) {
    const line = lines[index];
    const fence = line.match(/^\s*```([^`]*)\s*$/);
    if (fence) {
      flushParagraph();
      closeList();
      const codeLines = [];
      index += 1;
      while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length) index += 1;

      const block = document.createElement('div');
      block.className = 'code-block';
      const toolbar = document.createElement('div');
      toolbar.className = 'code-toolbar';
      const language = document.createElement('span');
      language.textContent = fence[1].trim() || 'CODE';
      const copyButton = document.createElement('button');
      copyButton.className = 'copy-code';
      copyButton.type = 'button';
      copyButton.textContent = 'Copy';
      copyButton.setAttribute('aria-label', 'Copy code');
      const codeText = codeLines.join('\n');
      copyButton.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(codeText);
          copyButton.textContent = 'Copied';
          window.setTimeout(() => { copyButton.textContent = 'Copy'; }, 1500);
        } catch {
          copyButton.textContent = 'Select code to copy';
        }
      });
      toolbar.append(language, copyButton);
      const pre = document.createElement('pre');
      const code = document.createElement('code');
      code.textContent = codeText;
      pre.append(code);
      block.append(toolbar, pre);
      container.append(block);
      continue;
    }

    if (!line.trim()) {
      flushParagraph();
      closeList();
      index += 1;
      continue;
    }

    const heading = line.match(/^#{1,6}\s+(.+)$/);
    if (heading) {
      flushParagraph();
      closeList();
      const h = document.createElement('h3');
      h.className = 'answer-heading';
      appendInlineMarkdown(h, heading[1]);
      container.append(h);
      index += 1;
      continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (bullet || ordered) {
      flushParagraph();
      const kind = bullet ? 'ul' : 'ol';
      if (!list || list.tagName.toLowerCase() !== kind) {
        closeList();
        list = document.createElement(kind);
        list.className = 'answer-list';
      }
      const item = document.createElement('li');
      appendInlineMarkdown(item, (bullet || ordered)[1]);
      list.append(item);
      index += 1;
      continue;
    }

    closeList();
    paragraph.push(line.trim());
    index += 1;
  }
  flushParagraph();
  closeList();
}

function makeMessage(role, text) {
  const row = document.createElement('article');
  row.className = `message ${role}`;

  if (role === 'assistant') {
    const avatar = document.createElement('span');
    avatar.className = 'avatar';
    avatar.setAttribute('aria-hidden', 'true');
    avatar.textContent = '✳';
    row.append(avatar);
  }

  const body = document.createElement('div');
  body.className = 'message-body';
  if (role === 'assistant') {
    const name = document.createElement('p');
    name.className = 'message-name';
    name.textContent = 'CloudOps Assistant';
    body.append(name);
  }
  if (role === 'assistant') {
    renderMarkdown(body, text);
  } else {
    const copy = document.createElement('p');
    copy.className = 'message-copy';
    copy.textContent = text;
    body.append(copy);
  }
  row.append(body);
  return { row, body };
}

function addSources(body, data) {
  const sources = Array.isArray(data.sources) ? data.sources : [];
  const meta = document.createElement('div');
  meta.className = 'answer-meta';

  if (Number.isFinite(data.retrieved_chunks)) {
    const count = document.createElement('span');
    count.className = 'meta-pill';
    count.textContent = `${data.retrieved_chunks} source${data.retrieved_chunks === 1 ? '' : 's'} retrieved`;
    meta.append(count);
  }
  if (Number.isFinite(data.processing_time_ms)) {
    const duration = document.createElement('span');
    duration.className = 'meta-pill';
    duration.textContent = `${(data.processing_time_ms / 1000).toFixed(1)}s`;
    meta.append(duration);
  }
  if (meta.childElementCount) body.append(meta);

  const details = document.createElement('details');
  details.className = 'sources';
  const summary = document.createElement('summary');
  summary.textContent = `View sources (${sources.length})`;
  details.append(summary);
  if (sources.length) {
    const list = document.createElement('ul');
    list.className = 'source-list';
    for (const source of sources) {
      const item = document.createElement('li');
      item.className = 'source-item';
      const parts = [source.technology, source.document, source.chunk_id].filter(Boolean);
      const label = parts.length ? parts.join(' · ') : 'Indexed document';
      if (source.source_url) {
        const link = document.createElement('a');
        link.href = source.source_url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = label;
        item.append(link);
      } else {
        item.textContent = label;
      }
      list.append(item);
    }
    details.append(list);
  } else {
    const note = document.createElement('p');
    note.className = 'message-copy';
    note.textContent = 'No source details were returned for this answer.';
    details.append(note);
  }
  body.append(details);
}

async function sendQuestion(question) {
  const trimmed = question.trim();
  if (!trimmed || sendButton.disabled) return;

  welcomeCard.hidden = true;
  messages.append(makeMessage('user', trimmed).row);
  const pending = makeMessage('assistant', '');
  pending.row.classList.add('pending');
  pending.body.querySelectorAll('.message-copy').forEach((copy) => copy.remove());
  const dots = document.createElement('div');
  dots.className = 'loading-dots';
  dots.setAttribute('aria-label', 'Thinking');
  dots.innerHTML = '<span></span><span></span><span></span>';
  pending.body.append(dots);
  messages.append(pending.row);
  input.value = '';
  sendButton.disabled = true;
  input.disabled = true;
  scrollToLatest();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: trimmed }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof data.detail === 'string' ? data.detail : `Request failed (${response.status}).`;
      throw new Error(detail);
    }
    pending.row.remove();
    const answer = makeMessage('assistant', data.answer || 'The service returned an empty answer.');
    addSources(answer.body, data);
    messages.append(answer.row);
  } catch (error) {
    pending.row.remove();
    const failure = makeMessage('assistant', 'I could not complete that request. Please try again in a moment.');
    const note = document.createElement('div');
    note.className = 'error-card';
    note.textContent = error.message || 'The service could not be reached.';
    failure.body.append(note);
    messages.append(failure.row);
  } finally {
    sendButton.disabled = false;
    input.disabled = false;
    input.focus();
    scrollToLatest();
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  sendQuestion(input.value);
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 125)}px`;
});

document.querySelectorAll('[data-prompt]').forEach((button) => {
  button.addEventListener('click', () => sendQuestion(button.dataset.prompt));
});

newChatButton.addEventListener('click', () => {
  messages.replaceChildren();
  welcomeCard.hidden = false;
  input.value = '';
  input.focus();
});

fetch('/health')
  .then((response) => {
    if (!response.ok) throw new Error('Service unavailable');
    serviceStatus.classList.add('is-online');
    statusText.textContent = 'Service online';
  })
  .catch(() => {
    serviceStatus.classList.add('is-offline');
    statusText.textContent = 'Service unavailable';
  });
