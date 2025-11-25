// Chat history management
let chatHistory = [];
let currentChatId = null;

// Load chat history from localStorage
function loadChatHistory() {
  const saved = localStorage.getItem('chatHistory');
  if (saved) {
    chatHistory = JSON.parse(saved);
    renderChatHistory();
  }
}

// Save chat history to localStorage
function saveChatHistory() {
  localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

// Create new chat
function createNewChat() {
  const chatId = Date.now().toString();
  const newChat = {
    id: chatId,
    title: 'New Chat',
    messages: [],
    timestamp: new Date().toISOString()
  };
  chatHistory.unshift(newChat);
  currentChatId = chatId;
  saveChatHistory();
  renderChatHistory();
  clearChatWindow();
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
function renderChatHistory() {
  const historyContainer = document.getElementById('chat-history');
  historyContainer.innerHTML = '';

  chatHistory.forEach(chat => {
    const item = document.createElement('div');
    item.className = 'history-item';
    if (chat.id === currentChatId) {
      item.classList.add('active');
    }

    const date = new Date(chat.timestamp);
    const timeStr = formatTime(date);

    item.innerHTML = `
      <div class="history-item-title">${chat.title}</div>
      <div class="history-item-time">${timeStr}</div>
    `;

    item.addEventListener('click', () => {
      loadChat(chat.id);
      closeSidebar();
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

// Load specific chat
function loadChat(chatId) {
  const chat = chatHistory.find(c => c.id === chatId);
  if (!chat) return;

  currentChatId = chatId;
  const chatWindow = document.getElementById('chat-window');
  chatWindow.innerHTML = '';

  chat.messages.forEach(msg => {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${msg.type}-message`;
    messageEl.innerHTML = `
      <div class="avatar ${msg.type === 'bot' ? 'bot-avatar' : ''}">${msg.type === 'bot' ? 'AI' : 'ND'}</div>
      <div class="bubble">${msg.content}</div>
    `;
    chatWindow.appendChild(messageEl);
  });

  chatWindow.scrollTop = chatWindow.scrollHeight;
  renderChatHistory();
}

// Save message to current chat
function saveMessage(type, content) {
  if (!currentChatId) {
    createNewChat();
  }

  const chat = chatHistory.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages.push({ type, content, timestamp: new Date().toISOString() });

  // Update chat title based on first user message
  if (type === 'user' && chat.messages.filter(m => m.type === 'user').length === 1) {
    chat.title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
  }

  saveChatHistory();
  renderChatHistory();
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
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatWindow = document.getElementById("chat-window");
  const menuButton = document.getElementById("menu-button");
  const closeSidebarBtn = document.getElementById("close-sidebar");
  const overlay = document.getElementById("overlay");
  const newChatBtn = document.getElementById("new-chat");

  // Load chat history
  loadChatHistory();

  // If no chat exists, create one
  if (chatHistory.length === 0) {
    createNewChat();
  } else {
    currentChatId = chatHistory[0].id;
    loadChat(currentChatId);
  }

  // Sidebar controls
  menuButton.addEventListener("click", openSidebar);
  closeSidebarBtn.addEventListener("click", closeSidebar);
  overlay.addEventListener("click", closeSidebar);
  newChatBtn.addEventListener("click", () => {
    createNewChat();
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

    // Save user message
    saveMessage('user', userInput);

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

      // Save bot message
      saveMessage('bot', answerText);

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
      saveMessage('bot', errorMessage);

      console.error("Error fetching API:", error);
    }

    // Scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
    input.focus();
  });
});