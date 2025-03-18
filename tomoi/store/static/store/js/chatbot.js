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