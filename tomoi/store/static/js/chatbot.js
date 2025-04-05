document.addEventListener('DOMContentLoaded', function () {
    // Biến theo dõi trạng thái chatbot
    let isChatbotOpen = false;
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const closeButton = document.querySelector('.chatbot-close');
    const messagesList = document.querySelector('.chatbot-messages');
    const messageInput = document.querySelector('.chatbot-input-field');
    const sendButton = document.querySelector('.chatbot-send-button');

    // Lấy sessionId từ localStorage hoặc tạo mới
    const chatSessionId = localStorage.getItem('chatSessionId') || generateSessionId();
    localStorage.setItem('chatSessionId', chatSessionId);

    // Lấy lịch sử chat từ localStorage
    let chatHistory = loadChatHistory();

    // Cấu hình và trạng thái chatbot
    const chatbotConfig = {
        api_key: document.querySelector('#chatbot-config').dataset.apiKey || '',
        model: document.querySelector('#chatbot-config').dataset.model || 'gemini-2.0-flash',
        max_tokens: parseInt(document.querySelector('#chatbot-config').dataset.maxTokens || '2048'),
        temperature: parseFloat(document.querySelector('#chatbot-config').dataset.temperature || '0.7')
    };

    // Mở chatbot khi nhấn vào nút toggle
    chatbotToggle.addEventListener('click', function (e) {
        e.preventDefault();
        // Toggle trạng thái hiển thị
        toggleChatbot();
    });

    // Đóng chatbot khi nhấn nút đóng
    closeButton.addEventListener('click', function () {
        toggleChatbot(false);
    });

    // Gửi tin nhắn khi nhấn nút gửi
    sendButton.addEventListener('click', function () {
        sendMessage();
    });

    // Gửi tin nhắn khi nhấn Enter
    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    // Toggle hiển thị chatbot
    function toggleChatbot(forcedState) {
        isChatbotOpen = forcedState !== undefined ? forcedState : !isChatbotOpen;

        if (isChatbotOpen) {
            chatbotContainer.classList.add('open');

            // Khôi phục lịch sử tin nhắn từ chatHistory
            restoreChatHistory();

            // Nếu chưa có tin nhắn nào, hiển thị tin nhắn chào mừng
            if (messagesList.children.length === 0) {
                addWelcomeMessage();
            }

            // Focus vào ô nhập tin nhắn
            setTimeout(() => {
                messageInput.focus();
            }, 300);
        } else {
            chatbotContainer.classList.remove('open');
        }
    }

    // Tạo mã phiên ngẫu nhiên
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    }

    // Lưu lịch sử chat vào localStorage
    function saveChatHistory() {
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }

    // Tải lịch sử chat từ localStorage
    function loadChatHistory() {
        const savedHistory = localStorage.getItem('chatHistory');
        return savedHistory ? JSON.parse(savedHistory) : [];
    }

    // Khôi phục lịch sử tin nhắn lên giao diện
    function restoreChatHistory() {
        // Xóa tất cả tin nhắn hiện tại
        messagesList.innerHTML = '';

        // Hiển thị lại các tin nhắn từ lịch sử
        chatHistory.forEach(message => {
            addMessageToChat(message, false); // false nghĩa là không lưu lại lịch sử (vì đang khôi phục từ lịch sử)
        });

        // Cuộn xuống tin nhắn cuối cùng
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    // Thêm tin nhắn chào mừng
    function addWelcomeMessage() {
        const welcomeMessage = {
            role: 'assistant',
            content: 'Xin chào! Tôi là trợ lý ảo của TomOi. Tôi có thể giúp bạn tìm hiểu về sản phẩm, dịch vụ hoặc giải đáp thắc mắc. Bạn cần hỗ trợ gì?'
        };
        addMessageToChat(welcomeMessage);
    }

    // Thêm tin nhắn vào khung chat
    function addMessageToChat(message, shouldSave = true) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chatbot-message');
        messageElement.classList.add(message.role === 'user' ? 'user-message' : 'assistant-message');

        // Xử lý nội dung tin nhắn
        let messageContent = message.content;

        // Kiểm tra nếu tin nhắn có chứa markdown hoặc HTML
        if (messageContent.includes('```') || messageContent.includes('<')) {
            // Chuyển đổi markdown thành HTML
            messageContent = convertMarkdownToHtml(messageContent);
        }

        messageElement.innerHTML = `
            <div class="message-content">${messageContent}</div>
        `;

        messagesList.appendChild(messageElement);

        // Cuộn xuống tin nhắn mới nhất
        messagesList.scrollTop = messagesList.scrollHeight;

        // Lưu vào lịch sử nếu cần
        if (shouldSave) {
            chatHistory.push(message);
            saveChatHistory();
        }
    }

    // Gửi tin nhắn
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Thêm tin nhắn của người dùng vào khung chat
        const userMessage = {
            role: 'user',
            content: message
        };
        addMessageToChat(userMessage);

        // Xóa nội dung input
        messageInput.value = '';

        // Hiển thị đang nhập
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('chatbot-message', 'assistant-message', 'typing-indicator');
        typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        messagesList.appendChild(typingIndicator);
        messagesList.scrollTop = messagesList.scrollHeight;

        try {
            // Gửi tin nhắn đến server
            const response = await fetch('/chatbot/process/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    type: 'text',
                    session_id: chatSessionId,
                    history: chatHistory
                })
            });

            const data = await response.json();

            // Xóa typing indicator
            messagesList.removeChild(typingIndicator);

            // Thêm phản hồi từ chatbot
            if (data.success) {
                const assistantMessage = {
                    role: 'assistant',
                    content: data.response
                };
                addMessageToChat(assistantMessage);

                // Nếu có special_content, hiển thị nó
                if (data.special_content) {
                    const specialContentElement = document.createElement('div');
                    specialContentElement.classList.add('chatbot-message', 'assistant-message', 'special-content');
                    specialContentElement.innerHTML = data.special_content;
                    messagesList.appendChild(specialContentElement);
                    messagesList.scrollTop = messagesList.scrollHeight;
                }
            } else {
                const errorMessage = {
                    role: 'assistant',
                    content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.'
                };
                addMessageToChat(errorMessage);
            }
        } catch (error) {
            // Xóa typing indicator
            messagesList.removeChild(typingIndicator);

            // Hiển thị lỗi
            const errorMessage = {
                role: 'assistant',
                content: 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối internet và thử lại.'
            };
            addMessageToChat(errorMessage);
            console.error('Error:', error);
        }
    }

    // Chuyển đổi markdown thành HTML
    function convertMarkdownToHtml(markdown) {
        // Xử lý code blocks
        markdown = markdown.replace(/```(.*?)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

        // Xử lý inline code
        markdown = markdown.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Xử lý headers
        markdown = markdown.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        markdown = markdown.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        markdown = markdown.replace(/^# (.*$)/gm, '<h1>$1</h1>');

        // Xử lý bold
        markdown = markdown.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Xử lý italic
        markdown = markdown.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Xử lý links
        markdown = markdown.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Xử lý danh sách không thứ tự
        markdown = markdown.replace(/^\* (.*$)/gm, '<li>$1</li>');
        markdown = markdown.replace(/<\/li>\n<li>/g, '</li><li>');
        markdown = markdown.replace(/<li>(.+?)(\n\n)/g, '<ul><li>$1</li></ul>$2');

        // Xử lý xuống dòng
        markdown = markdown.replace(/\n/g, '<br>');

        return markdown;
    }

    // Lấy CSRF token
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

    // Xóa lịch sử chat
    function clearChatHistory() {
        chatHistory = [];
        localStorage.removeItem('chatHistory');
        messagesList.innerHTML = '';
        addWelcomeMessage();
    }

    // Nếu cần, thêm một nút xóa lịch sử
    const resetButton = document.querySelector('.chatbot-reset');
    if (resetButton) {
        resetButton.addEventListener('click', function () {
            clearChatHistory();
        });
    }
}); 