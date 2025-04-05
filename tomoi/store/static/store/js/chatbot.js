// Thêm biến để kiểm soát chế độ chat
let isChatWithAdmin = false;

// Sửa phần gửi tin nhắn để sử dụng API công khai
function sendChatbotMessage(message) {
    // Hiển thị tin nhắn người dùng
    displayUserMessage(message);

    // Hiển thị trạng thái đang nhập
    showTypingIndicator();

    console.log("Gửi tin nhắn đến API:", message);

    // Gửi tin nhắn đến API công khai
    fetch('/accounts/api/public/chatbot-process/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            message: message
        })
    })
        .then(response => {
            console.log("Nhận response từ server, status:", response.status);
            return response.json();
        })
        .then(data => {
            // Ẩn trạng thái đang nhập
            hideTypingIndicator();

            console.log("Dữ liệu trả về:", data);

            if (data.success) {
                // Hiển thị phản hồi từ chatbot
                displayBotMessage(data.response);
            } else {
                // Hiển thị lỗi
                console.error("Lỗi từ API:", data.message);
                displayErrorMessage(data.message || 'Đã xảy ra lỗi khi xử lý tin nhắn');
            }
        })
        .catch(error => {
            // Ẩn trạng thái đang nhập
            hideTypingIndicator();
            console.error('Lỗi khi gửi tin nhắn:', error);
            displayErrorMessage('Không thể kết nối đến máy chủ. Vui lòng thử lại sau.');
        });
}

// Hàm lấy CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Hàm hiển thị tin nhắn người dùng
function displayUserMessage(message) {
    const chatMessages = document.querySelector('.chatbot-messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'user-message';
    messageElement.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hàm hiển thị tin nhắn bot
function displayBotMessage(message) {
    const chatMessages = document.querySelector('.chatbot-messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'bot-message';
    messageElement.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hàm hiển thị lỗi
function displayErrorMessage(message) {
    const chatMessages = document.querySelector('.chatbot-messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'system-message error';
    messageElement.innerHTML = `<p>${message}</p>`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hiển thị trạng thái đang nhập
function showTypingIndicator() {
    const chatMessages = document.querySelector('.chatbot-messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Ẩn trạng thái đang nhập
function hideTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Thêm hàm khởi tạo UI ban đầu
function initializeChatbotUI() {
    console.log("Initializing chatbot UI");

    // Kiểm tra xem chatbot container đã tồn tại chưa
    const chatbotContainer = document.getElementById('tomoi-chatbot');
    if (!chatbotContainer) {
        console.error("Chatbot container not found");
        return;
    }

    // Kiểm tra và hiển thị cấu trúc HTML của chatbot
    console.log("Chatbot HTML structure:", chatbotContainer.innerHTML);

    // Kiểm tra phần tử tiêu đề
    const chatbotTitle = document.querySelector('.chatbot-header-title');
    if (!chatbotTitle) {
        console.warn("Creating missing chatbot title element");
        // Tạo phần tử tiêu đề nếu chưa có
        const headerTitle = document.createElement('div');
        headerTitle.className = 'chatbot-header-title';
        headerTitle.textContent = chatbotContainer.getAttribute('data-chatbot-name') || 'TomOi Assistant';

        const chatbotHeader = document.querySelector('.chatbot-header');
        if (chatbotHeader) {
            chatbotHeader.insertBefore(headerTitle, chatbotHeader.firstChild);
        }
    }
}

// Sửa lại hàm khởi tạo DOM elements
function initChat() {
    cacheElements();
    fetchChatbotConfig();

    // Gắn event cho chat launcher
    const chatLauncher = document.getElementById('chat-launcher');
    if (chatLauncher) {
        // Sửa lỗi bấm lần đầu tự tắt
        chatLauncher.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("Launcher clicked");
            openChatWindow(); // Luôn mở cửa sổ chat khi bấm
        });
    }

    // Gắn event cho form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const chatInput = document.getElementById('chat-input');
            if (chatInput && chatInput.value.trim()) {
                const message = chatInput.value.trim();
                chatInput.value = '';
                // Chỉ thêm và gửi một lần
                addUserMessage(message);

                // Kiểm tra xem đang nhắn tin với admin hay chatbot
                if (isChatWithAdmin) {
                    sendMessageToAdmin(message);
                } else {
                    sendMessageToAPI(message);
                }
            }
        });
    }

    // Thêm nút chuyển đổi giữa TomAI và Admin
    addSwitchButton();

    // Xử lý lại các nút gợi ý để tránh lặp gửi 2 lần
    setupSuggestionButtons();
}

// Tách riêng hàm để xử lý các nút gợi ý
function setupSuggestionButtons() {
    console.log("Setting up suggestion buttons");

    // Xóa tất cả event listeners hiện có
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        // Tạo bản sao của nút để loại bỏ tất cả event listeners
        const newBtn = btn.cloneNode(true);
        if (btn.parentNode) {
            btn.parentNode.replaceChild(newBtn, btn);
        }

        // Thêm event listener mới với { once: true } để đảm bảo chỉ kích hoạt một lần
        newBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            // Ngăn chặn xử lý nếu nút đã bị vô hiệu hóa
            if (this.disabled) {
                console.log('Button already disabled, ignoring click');
                return;
            }

            const text = this.getAttribute('data-text');
            if (!text) return;

            console.log("Suggestion clicked:", text);

            // Vô hiệu hóa nút ngay lập tức để tránh double-click
            this.disabled = true;

            // Thêm tin nhắn vào giao diện
            addUserMessage(text);

            // Gửi tin nhắn đến API
            sendMessageToAPI(text);

            // Ẩn tất cả các nút gợi ý sau khi nhấn
            const suggestionsContainer = document.querySelector('.message.bot.suggestions');
            if (suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
        }, { once: true }); // once: true đảm bảo event listener chỉ chạy một lần
    });
}

// Sửa lại hàm hiển thị gợi ý
function displaySuggestions() {
    const messagesContainer = document.querySelector('.chat-messages');
    if (!messagesContainer) return;

    // Xóa tất cả gợi ý cũ
    const existingSuggestions = messagesContainer.querySelector('.message.bot.suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }

    // Tạo phần gợi ý mới
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'message bot suggestions';
    suggestionsDiv.innerHTML = `
        <div class="message-avatar">
            <img src="${document.querySelector('.chat-avatar img')?.src || '/static/store/images/chatbot-avatar.png'}" alt="Bot">
        </div>
        <div class="message-content">
            <div class="message-text">Bạn có thể hỏi tôi:</div>
            <div class="suggestion-buttons">
                <button class="suggestion-btn" data-text="Có sản phẩm nào đang khuyến mãi?">Có sản phẩm nào đang khuyến mãi?</button>
                <button class="suggestion-btn" data-text="Tôi muốn tìm ứng dụng giải trí">Tôi muốn tìm ứng dụng giải trí</button>
                <button class="suggestion-btn" data-text="Làm thế nào để đổi mật khẩu?">Làm thế nào để đổi mật khẩu?</button>
            </div>
        </div>
    `;
    messagesContainer.appendChild(suggestionsDiv);

    // Thiết lập event handlers cho các nút gợi ý
    setupSuggestionButtons();

    // Cuộn xuống cuối
    scrollToBottom();
}

// Thêm hàm để gửi tin nhắn đến admin
function sendMessageToAdmin(message) {
    // Hiển thị trạng thái đang nhập
    showTypingIndicator();

    console.log("Gửi tin nhắn đến Admin:", message);

    // Gửi tin nhắn đến API admin chat
    fetch('/accounts/api/user-chat/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            message: message
        })
    })
        .then(response => {
            console.log("Nhận response từ server admin chat, status:", response.status);
            return response.json();
        })
        .then(data => {
            // Ẩn trạng thái đang nhập
            hideTypingIndicator();

            console.log("Dữ liệu trả về từ admin chat:", data);

            if (data.success) {
                // Nếu thành công, không cần hiển thị phản hồi vì admin sẽ trả lời sau
                // Hiển thị tin nhắn xác nhận đã gửi
                displaySystemMessage("Tin nhắn đã được gửi đến Admin. Vui lòng chờ phản hồi.");
            } else {
                // Hiển thị lỗi
                console.error("Lỗi từ API admin chat:", data.message);
                displayErrorMessage(data.message || 'Đã xảy ra lỗi khi gửi tin nhắn');
            }
        })
        .catch(error => {
            // Ẩn trạng thái đang nhập
            hideTypingIndicator();
            console.error('Lỗi khi gửi tin nhắn đến admin:', error);
            displayErrorMessage('Không thể kết nối đến máy chủ. Vui lòng thử lại sau.');
        });
}

// Thêm hàm để hiển thị nút chuyển đổi
function addSwitchButton() {
    const chatMessages = document.querySelector('.chat-messages');
    if (!chatMessages) return;

    // Tạo container cho nút chuyển đổi
    const switchContainer = document.createElement('div');
    switchContainer.className = 'chat-switch-container';
    switchContainer.style.display = 'flex';
    switchContainer.style.justifyContent = 'center';
    switchContainer.style.margin = '10px 0';
    switchContainer.style.gap = '10px';

    // Tạo nút "Nhắn tin với Admin"
    const chatWithAdminBtn = document.createElement('button');
    chatWithAdminBtn.className = 'chat-switch-btn chat-with-admin';
    chatWithAdminBtn.textContent = 'Nhắn tin với Admin';
    chatWithAdminBtn.style.padding = '8px 15px';
    chatWithAdminBtn.style.backgroundColor = '#e50914';
    chatWithAdminBtn.style.color = 'white';
    chatWithAdminBtn.style.border = 'none';
    chatWithAdminBtn.style.borderRadius = '20px';
    chatWithAdminBtn.style.cursor = 'pointer';
    chatWithAdminBtn.style.fontSize = '14px';
    chatWithAdminBtn.style.fontWeight = '500';
    chatWithAdminBtn.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';

    // Tạo nút "Nhắn tin với TomAI"
    const chatWithAIBtn = document.createElement('button');
    chatWithAIBtn.className = 'chat-switch-btn chat-with-ai';
    chatWithAIBtn.textContent = 'Nhắn tin với TomAI';
    chatWithAIBtn.style.padding = '8px 15px';
    chatWithAIBtn.style.backgroundColor = '#ebebeb';
    chatWithAIBtn.style.color = '#333';
    chatWithAIBtn.style.border = 'none';
    chatWithAIBtn.style.borderRadius = '20px';
    chatWithAIBtn.style.cursor = 'pointer';
    chatWithAIBtn.style.fontSize = '14px';
    chatWithAIBtn.style.fontWeight = '500';
    chatWithAIBtn.style.display = 'none'; // Ban đầu ẩn nút này

    // Gắn sự kiện cho nút "Nhắn tin với Admin"
    chatWithAdminBtn.addEventListener('click', function () {
        isChatWithAdmin = true;
        this.style.display = 'none';
        chatWithAIBtn.style.display = 'block';

        // Xóa lịch sử chat hiện tại
        clearChatHistory();

        // Hiển thị tin nhắn thông báo chuyển chế độ
        displaySystemMessage("Đã chuyển sang chế độ nhắn tin với Admin. Tin nhắn của bạn sẽ được gửi đến Admin của TomOi.");

        // Cập nhật tiêu đề
        updateChatTitle("Chat với Admin");
    });

    // Gắn sự kiện cho nút "Nhắn tin với TomAI"
    chatWithAIBtn.addEventListener('click', function () {
        isChatWithAdmin = false;
        this.style.display = 'none';
        chatWithAdminBtn.style.display = 'block';

        // Xóa lịch sử chat hiện tại
        clearChatHistory();

        // Hiển thị tin nhắn chào mừng
        displaySystemMessage("Đã chuyển sang chế độ nhắn tin với TomAI. Tôi là trợ lý ảo của TomOi, tôi có thể giúp gì cho bạn?");

        // Hiển thị các gợi ý
        displaySuggestions();

        // Cập nhật tiêu đề
        updateChatTitle("Chat với TomAI");
    });

    // Thêm nút vào container
    switchContainer.appendChild(chatWithAdminBtn);
    switchContainer.appendChild(chatWithAIBtn);

    // Thêm container vào chatbot
    const chatHeader = document.querySelector('.chat-header');
    if (chatHeader && chatHeader.parentNode) {
        chatHeader.parentNode.insertBefore(switchContainer, chatHeader.nextSibling);
    }
}

// Hàm để xóa lịch sử chat
function clearChatHistory() {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        // Giữ lại container nhưng xóa tất cả tin nhắn
        while (chatMessages.firstChild) {
            chatMessages.removeChild(chatMessages.firstChild);
        }
    }
}

// Thêm hàm để cập nhật tiêu đề chat
function updateChatTitle(title) {
    const chatTitle = document.querySelector('.chat-header-title');
    if (chatTitle) {
        chatTitle.textContent = title;
    }
}

// Hàm hiển thị tin nhắn hệ thống
function displaySystemMessage(message) {
    const chatMessages = document.querySelector('.chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'system-message';
    messageElement.innerHTML = `<p>${message}</p>`;
    messageElement.style.backgroundColor = '#f8f9fa';
    messageElement.style.color = '#666';
    messageElement.style.textAlign = 'center';
    messageElement.style.padding = '8px 12px';
    messageElement.style.margin = '10px auto';
    messageElement.style.borderRadius = '10px';
    messageElement.style.maxWidth = '90%';
    messageElement.style.fontSize = '0.9rem';

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
} 