// Hàm hiển thị text từng chữ 1 với delay
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

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("user-input");
  const chatWindow = document.querySelector(".chat-window");

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const userInput = input.value.trim();
    if (!userInput) return;

    // Thêm tin nhắn người dùng vào màn hình
    const userMessageEl = document.createElement("div");
    userMessageEl.className = "message user-message";
    userMessageEl.innerHTML = `
      <div class="avatar">ND</div>
      <div class="bubble">${userInput}</div>
    `;
    chatWindow.appendChild(userMessageEl);

    // Tạo placeholder tin nhắn bot với avatar và bubble rỗng
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

    // Cuộn xuống cuối chat
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Gửi request đến server python API
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userInput }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      // Giả sử API trả về JSON { answer: "text trả về" }
      const data = await response.json();

      // Hiển thị kết quả trả về hiệu ứng gõ chữ
      await typeEffect(botBubble, data.answer || "No response from server.");

    } catch (error) {
      await typeEffect(botBubble, "Sorry, there was a problem with the server.");
      console.error("Error fetching API:", error);
    }

    // Cuộn thêm lần nữa để thấy hết tin nhắn bot
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Xóa input sau khi gửi
    input.value = "";
    input.focus();
  });
});