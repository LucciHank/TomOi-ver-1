document.addEventListener('DOMContentLoaded', function() {
    // Các biến và tham chiếu DOM
    const chatLauncher = document.getElementById('chat-launcher');
    const chatWindow = document.getElementById('chat-window');
    const btnClose = document.getElementById('btn-close');
    const btnMinimize = document.getElementById('btn-minimize');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const notificationBadge = document.getElementById('notification-badge');
    
    // Thiết lập session ID duy nhất cho cuộc trò chuyện
    const sessionId = generateSessionId();
    
    // Biến lưu trữ lịch sử trò chuyện
    let chatHistory = [];
    
    // Khởi tạo chatbot
    initialize();
    
    function initialize() {
        // Hiển thị thông báo để người dùng biết có chatbot
        setTimeout(() => {
            notificationBadge.style.display = 'flex';
        }, 3000);
        
        // Hiệu ứng rung sau vài giây
        setTimeout(() => {
            const chatLauncher = document.getElementById('chat-launcher');
            chatLauncher.classList.add('shake');
            setTimeout(() => {
                chatLauncher.classList.remove('shake');
            }, 1000);
            
            // Hiển thị thông báo
            notificationBadge.style.display = 'flex';
        }, 3000);
        
        // Gắn sự kiện cho các nút gợi ý
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const text = this.getAttribute('data-text');
                sendMessage(text);
            });
        });
        
        // Đặt chiều cao tối đa cho khung tin nhắn trên thiết bị di động
        setMaxHeightOnMobile();
        window.addEventListener('resize', setMaxHeightOnMobile);
        
        // Khôi phục lịch sử trò chuyện từ localStorage nếu có
        loadChatHistory();
        
        // Debug - kiểm tra xem các phần tử có tồn tại không
        console.log("Chat launcher exists:", !!chatLauncher);
        console.log("Chat window exists:", !!chatWindow);
    }
    
    // Mở/đóng cửa sổ chat
    chatLauncher.addEventListener('click', function(e) {
        console.log("Chat launcher clicked");
        toggleChatWindow();
    });
    
    btnClose.addEventListener('click', toggleChatWindow);
    btnMinimize.addEventListener('click', toggleChatWindow);
    
    // Xử lý gửi tin nhắn
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(message);
            chatInput.value = '';
        }
    });
    
    function toggleChatWindow() {
        console.log("Toggle chat window called");
        console.log("Current display:", chatWindow.style.display);
        
        if (chatWindow.style.display === 'none' || chatWindow.style.display === '') {
            chatWindow.style.display = 'flex';
            setTimeout(() => {
                chatWindow.classList.add('active');
            }, 10);
            notificationBadge.style.display = 'none';
            scrollToBottom();
            chatInput.focus();
        } else {
            chatWindow.classList.remove('active');
            setTimeout(() => {
                chatWindow.style.display = 'none';
            }, 300);
        }
    }
    
    function sendMessage(message) {
        // Hiển thị tin nhắn của người dùng
        addMessage('user', message);
        
        // Hiển thị chỉ báo đang nhập
        showTypingIndicator();
        
        // Gửi yêu cầu đến API
        sendToAPI(message);
    }
    
    function sendToAPI(message) {
        // Thêm vào lịch sử trò chuyện
        chatHistory.push({
            role: 'user',
            content: message
        });
        
        // Lưu lịch sử chat vào localStorage
        saveAndLogChatHistory();
        
        // Gửi API request
        fetch('/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                history: chatHistory
            })
        })
        .then(response => response.json())
        .then(data => {
            // Xóa chỉ báo đang nhập
            removeTypingIndicator();
            
            if (data.success) {
                // Hiển thị phản hồi từ bot
                addMessage('bot', data.response);
                
                // Thêm vào lịch sử trò chuyện
                chatHistory.push({
                    role: 'assistant',
                    content: data.response
                });
                
                // Lưu lịch sử chat
                saveAndLogChatHistory();
                
                // Hiển thị sản phẩm nếu có
                if (data.products && data.products.length > 0) {
                    addProductsMessage(data.products);
                }
            } else {
                // Hiển thị thông báo lỗi
                addMessage('bot', data.error || 'Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage('bot', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn.');
        });
    }
    
    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        if (type === 'bot') {
            const avatarImg = document.querySelector('.chat-avatar img').src;
            
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <img src="${avatarImg}" alt="Bot">
                </div>
                <div class="message-content">
                    <div class="message-text">${content}</div>
                    <div class="message-time">${currentTime}</div>
                </div>
            `;
        } else {
            // Tin nhắn người dùng
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${content}</div>
                    <div class="message-time">${currentTime}</div>
                </div>
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        
        // Đảm bảo luôn cuộn xuống tin nhắn mới nhất
        setTimeout(() => {
            scrollToBottom();
        }, 100);
    }
    
    function addProductsMessage(products) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot products';
        
        let productsHTML = '<div class="product-cards">';
        products.forEach(product => {
            const price = parseFloat(product.price).toLocaleString('vi-VN') + '₫';
            const thumbnail = product.thumbnail || '/static/images/no-image.png';
            
            productsHTML += `
                <div class="product-card">
                    <div class="product-card-image">
                        <img src="${thumbnail}" alt="${product.name}">
                    </div>
                    <div class="product-card-content">
                        <div class="product-card-name">${product.name}</div>
                        <div class="product-card-price">${price}</div>
                        <a href="${product.url}" class="product-card-btn">Xem chi tiết</a>
                    </div>
                </div>
            `;
        });
        productsHTML += '</div>';
        
        const avatarImg = document.querySelector('.chat-avatar img').src;
        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <img src="${avatarImg}" alt="Bot">
            </div>
            <div class="message-content">
                <div class="message-text">Đây là một số sản phẩm bạn có thể quan tâm:</div>
                ${productsHTML}
                <div class="message-time">${currentTime}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function addCategoryOptionsMessage(categories) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        let categoriesHTML = '<div class="category-options">';
        categories.forEach(category => {
            categoriesHTML += `
                <button class="category-btn" data-category="${category.id}">${category.name}</button>
            `;
        });
        categoriesHTML += '</div>';
        
        const avatarImg = document.querySelector('.chat-avatar img').src;
        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <img src="${avatarImg}" alt="Bot">
            </div>
            <div class="message-content">
                <div class="message-text">Bạn muốn tìm thể loại nào?</div>
                ${categoriesHTML}
                <div class="message-time">${currentTime}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Gắn sự kiện cho các nút thể loại
        messageDiv.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const categoryId = this.getAttribute('data-category');
                const categoryName = this.textContent;
                
                // Đánh dấu nút được chọn
                document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Gửi lựa chọn của người dùng
                sendMessage(`Tôi muốn tìm sản phẩm thuộc thể loại: ${categoryName}`);
            });
        });
        
        scrollToBottom();
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-message';
        typingDiv.id = 'typing-indicator';
        
        const avatarImg = document.querySelector('.chat-avatar img').src;
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <img src="${avatarImg}" alt="Bot">
            </div>
            <div class="message-content">
                <div class="message-text typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
            console.log("Scrolled to bottom:", chatMessages.scrollHeight);
        }
    }
    
    function setMaxHeightOnMobile() {
        if (window.innerWidth <= 480) {
            const vh = window.innerHeight * 0.7;
            document.querySelector('.chat-body').style.maxHeight = `${vh}px`;
        } else {
            document.querySelector('.chat-body').style.maxHeight = '';
        }
    }
    
    function saveAndLogChatHistory() {
        // Lưu vào localStorage
        localStorage.setItem(`chat_history_${sessionId}`, JSON.stringify(chatHistory));
        
        // Gửi lên server để log
        fetch('/api/log-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                session_id: sessionId,
                history: chatHistory
            })
        }).catch(error => {
            console.error('Error logging chat history:', error);
        });
    }
    
    function loadChatHistory() {
        const saved = localStorage.getItem(`chat_history_${sessionId}`);
        if (saved) {
            try {
                chatHistory = JSON.parse(saved);
                
                // Hiển thị lại các tin nhắn đã lưu (tối đa 10 tin nhắn gần nhất)
                const recentMessages = chatHistory.slice(-10);
                recentMessages.forEach(msg => {
                    if (msg.role === 'user') {
                        addMessage('user', msg.content);
                    } else if (msg.role === 'assistant') {
                        addMessage('bot', msg.content);
                    }
                });
            } catch (e) {
                console.error('Error parsing chat history:', e);
                chatHistory = [];
            }
        }
    }
    
    function generateSessionId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
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
});