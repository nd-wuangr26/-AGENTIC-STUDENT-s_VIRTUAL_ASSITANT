// Authentication check
function checkUserAuth() {
  const token = localStorage.getItem('access_token');
  const role = localStorage.getItem('role');

  if (!token) {
    window.location.href = 'login.html';
    return false;
  }

  // If admin, redirect to admin dashboard
  if (role === 'admin') {
    window.location.href = 'admin.html';
    return false;
  }

  return true;
}

// Display username
function displayUserInfo() {
  const username = localStorage.getItem('username');
  if (username) {
    document.getElementById('username-display').textContent = username;
  }
}

// Logout function
function logout() {
  localStorage.clear();
  window.location.href = 'login.html';
}

// Check auth on page load
if (!checkUserAuth()) {
  // Will redirect, so stop execution
  throw new Error('Not authenticated');
}

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

function getAuthHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}

// Chat history management with database
let currentSessionId = null;

// Load chat history from database
async function loadChatHistory() {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      headers: getAuthHeaders()
    });

    if (response.ok) {
      const sessions = await response.json();
      renderChatHistory(sessions);

      // Load first session or create new one
      if (sessions.length > 0) {
        currentSessionId = sessions[0].session_id;
        await loadSession(currentSessionId);
      } else {
        await createNewChat();
      }
    }
  } catch (error) {
    console.error('Error loading chat history:', error);
  }
}

// Create new chat session
async function createNewChat() {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ title: 'New Chat' })
    });

    if (response.ok) {
      const newSession = await response.json();
      currentSessionId = newSession.session_id;
      await loadChatHistory();
      clearChatWindow();
    }
  } catch (error) {
    console.error('Error creating new chat:', error);
  }
}

// Clear chat window
function clearChatWindow() {
  const chatWindow = document.getElementById('chat-window');
  chatWindow.innerHTML = `
    <div class="message bot-message">
      <div class="avatar bot-avatar">AI</div>
      <div class="bubble">How can I help you today?</div>
    </div>
  `;
}

// Render chat history in sidebar
function renderChatHistory(sessions) {
  const historyContainer = document.getElementById('chat-history');
  historyContainer.innerHTML = '';

  sessions.forEach(session => {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.setAttribute('data-session-id', session.session_id);
    if (session.session_id === currentSessionId) {
      item.classList.add('active');
    }

    const date = new Date(session.updated_at);
    const timeStr = formatTime(date);

    item.innerHTML = `
      <div class="history-item-content">
        <div class="history-item-title">${session.title}</div>
        <div class="history-item-time">${timeStr}</div>
      </div>
      <button class="delete-session-btn" data-session-id="${session.session_id}" title="Delete">
        🗑️
      </button>
    `;

    item.querySelector('.history-item-content').addEventListener('click', async () => {
      await loadSession(session.session_id);
      closeSidebar();
    });

    // Delete button handler
    item.querySelector('.delete-session-btn').addEventListener('click', async (e) => {
      e.stopPropagation();
      if (confirm('Delete this chat?')) {
        await deleteSession(session.session_id);
      }
    });

    historyContainer.appendChild(item);
  });
}

// Format time
function formatTime(date) {
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

// Load specific session
async function loadSession(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      headers: getAuthHeaders()
    });

    if (response.ok) {
      const sessionData = await response.json();
      currentSessionId = sessionId;

      const chatWindow = document.getElementById('chat-window');
      chatWindow.innerHTML = '';

      sessionData.messages.forEach(msg => {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${msg.role === 'user' ? 'user' : 'bot'}-message`;
        messageEl.innerHTML = `
          <div class="avatar ${msg.role === 'assistant' ? 'bot-avatar' : ''}">${msg.role === 'assistant' ? 'AI' : 'ND'}</div>
          <div class="bubble">${msg.content}</div>
        `;
        chatWindow.appendChild(messageEl);
      });

      chatWindow.scrollTop = chatWindow.scrollHeight;

      // Update sidebar active state only
      document.querySelectorAll('.history-item').forEach(item => {
        item.classList.remove('active');
      });
      const activeItem = document.querySelector(`[data-session-id="${sessionId}"]`)?.closest('.history-item');
      if (activeItem) {
        activeItem.classList.add('active');
      }
    }
  } catch (error) {
    console.error('Error loading session:', error);
  }
}

// Save message to database
async function saveMessage(role, content) {
  if (!currentSessionId) {
    await createNewChat();
  }

  try {
    await fetch(`${API_BASE_URL}/chat/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        session_id: currentSessionId,
        role: role,
        content: content
      })
    });

    // Update session title based on first user message
    if (role === 'user') {
      const sessions = await (await fetch(`${API_BASE_URL}/chat/sessions`, {
        headers: getAuthHeaders()
      })).json();

      const currentSession = sessions.find(s => s.session_id === currentSessionId);
      if (currentSession && currentSession.message_count <= 1) {
        const title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
        await updateSessionTitle(currentSessionId, title);

        // Only refresh sidebar after title update
        await refreshSidebar();
      }
    }
  } catch (error) {
    console.error('Error saving message:', error);
  }
}

// Refresh sidebar only (không load lại session)
async function refreshSidebar() {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      headers: getAuthHeaders()
    });

    if (response.ok) {
      const sessions = await response.json();
      renderChatHistory(sessions);
    }
  } catch (error) {
    console.error('Error refreshing sidebar:', error);
  }
}

// Update session title
async function updateSessionTitle(sessionId, title) {
  try {
    await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/title?title=${encodeURIComponent(title)}`, {
      method: 'PUT',
      headers: getAuthHeaders()
    });
  } catch (error) {
    console.error('Error updating title:', error);
  }
}

// Delete session
async function deleteSession(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    if (response.ok) {
      // If deleting current session, create new one
      if (sessionId === currentSessionId) {
        await createNewChat();
      } else {
        await loadChatHistory();
      }
    }
  } catch (error) {
    console.error('Error deleting session:', error);
  }
}

// Delete all sessions
async function deleteAllSessions() {
  if (!confirm('Delete all chat history? This cannot be undone.')) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    if (response.ok) {
      await createNewChat();
    }
  } catch (error) {
    console.error('Error deleting all sessions:', error);
  }
}

// Typing effect
function typeEffect(element, text, delay = 30) {
  return new Promise((resolve) => {
    element.textContent = "";
    let i = 0;
    function type() {
      if (i < text.length) {
        element.textContent += text.charAt(i);
        i++;
        setTimeout(type, delay);
      } else {
        resolve();
      }
    }
    type();
  });
}

// Show typing indicator
function showTypingIndicator() {
  const chatWindow = document.getElementById('chat-window');
  const typingEl = document.createElement('div');
  typingEl.className = 'message bot-message typing-message';
  typingEl.innerHTML = `
    <div class="avatar bot-avatar">AI</div>
    <div class="bubble">
      <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;
  chatWindow.appendChild(typingEl);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return typingEl;
}

// Sidebar controls
function openSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('overlay').classList.add('active');
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('active');
}

// Initialize
document.addEventListener("DOMContentLoaded", async function () {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatWindow = document.getElementById("chat-window");
  const menuButton = document.getElementById("menu-button");
  const closeSidebarBtn = document.getElementById("close-sidebar");
  const overlay = document.getElementById("overlay");
  const newChatBtn = document.getElementById("new-chat");
  const logoutBtn = document.getElementById("logout-btn");

  // Display user info
  displayUserInfo();

  // Logout handler
  logoutBtn.addEventListener("click", logout);

  // Load chat history from database
  await loadChatHistory();

  // Sidebar controls
  menuButton.addEventListener("click", openSidebar);
  closeSidebarBtn.addEventListener("click", closeSidebar);
  overlay.addEventListener("click", closeSidebar);
  newChatBtn.addEventListener("click", async () => {
    await createNewChat();
    closeSidebar();
  });

  // Form submit
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const userInput = input.value.trim();
    if (!userInput) return;

    // Add user message
    const userMessageEl = document.createElement("div");
    userMessageEl.className = "message user-message";
    userMessageEl.innerHTML = `
      <div class="avatar">ND</div>
      <div class="bubble">${userInput}</div>
    `;
    chatWindow.appendChild(userMessageEl);

    // Save user message to database
    await saveMessage('user', userInput);

    // Show typing indicator
    const typingEl = showTypingIndicator();

    // Scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Clear input
    input.value = "";

    // Send request to server
    try {
      const response = await fetch("http://127.0.0.1:8000/api/generate/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userInput }),
      });

      // Remove typing indicator
      typingEl.remove();

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Check response structure and extract answer
      let answerText = "No response from server.";

      if (data.ok && data.answer) {
        answerText = data.answer;
      } else if (data.answer) {
        answerText = data.answer;
      } else if (data.error) {
        answerText = `Error: ${data.error}`;
      }

      // Create bot message element
      const botMessageEl = document.createElement("div");
      botMessageEl.className = "message bot-message";
      const botAvatar = document.createElement("div");
      botAvatar.className = "avatar bot-avatar";
      botAvatar.textContent = "AI";
      const botBubble = document.createElement("div");
      botBubble.className = "bubble";
      botMessageEl.appendChild(botAvatar);
      botMessageEl.appendChild(botBubble);
      chatWindow.appendChild(botMessageEl);

      // Type effect
      await typeEffect(botBubble, answerText);

      // Save bot message to database
      await saveMessage('assistant', answerText);

    } catch (error) {
      // Remove typing indicator if still present
      if (typingEl.parentNode) {
        typingEl.remove();
      }

      const errorMessage = `Sorry, there was a problem connecting to the server. Please make sure the backend is running on http://127.0.0.1:8000`;

      const botMessageEl = document.createElement("div");
      botMessageEl.className = "message bot-message";
      const botAvatar = document.createElement("div");
      botAvatar.className = "avatar bot-avatar";
      botAvatar.textContent = "AI";
      const botBubble = document.createElement("div");
      botBubble.className = "bubble";
      botMessageEl.appendChild(botAvatar);
      botMessageEl.appendChild(botBubble);
      chatWindow.appendChild(botMessageEl);

      await typeEffect(botBubble, errorMessage);
      await saveMessage('assistant', errorMessage);

      console.error("Error fetching API:", error);
    }

    // Scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
    input.focus();
  });
});