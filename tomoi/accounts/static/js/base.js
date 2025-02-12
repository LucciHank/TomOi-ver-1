// Cập nhật hàm updateCartDropdown để hiển thị thêm thông tin variant
function updateCartDropdown(cartItems) {
    const cartItemsContainer = document.querySelector('.cart-items');
    const emptyCart = document.querySelector('.empty-cart');
    const totalAmount = document.querySelector('.total-amount');

    if (!cartItems || cartItems.length === 0) {
        if (emptyCart) emptyCart.style.display = 'block';
        if (cartItemsContainer) cartItemsContainer.innerHTML = '';
        if (totalAmount) totalAmount.textContent = '0đ';
        return;
    }

    if (emptyCart) emptyCart.style.display = 'none';

    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = cartItems.map(item => `
            <div class="cart-item" data-id="${item.id}" data-stock="${item.stock}">
                <div class="item-image">
                    <img src="${item.image || '/static/images/placeholder.png'}" alt="${item.name}">
                </div>
                <div class="item-content">
                    <div class="item-info">
                        <h6 class="item-name">${item.name}</h6>
                        <div class="item-details">
                            ${item.variant_name ? `<small>Loại: ${item.variant_name}</small>` : ''}
                            ${item.duration ? `<small>Thời hạn: ${item.duration} tháng</small>` : ''}
                            ${item.upgrade_email ? `<small>Email: ${item.upgrade_email}</small>` : ''}
                        </div>
                        <div class="item-price">
                            <span class="current-price">${formatPrice(item.price)}</span>
                        </div>
                    </div>
                    <div class="item-controls">
                        <div class="quantity-controls">
                            <button class="quantity-btn minus">-</button>
                            <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="${item.stock}" readonly>
                            <button class="quantity-btn plus">+</button>
                        </div>
                        <button class="remove-btn" data-id="${item.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Cập nhật tổng tiền
    if (totalAmount) {
        const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        totalAmount.textContent = formatPrice(total);
    }
}

// Dropdown menu HTML
const dropdownHTML = `
    <div class="dropdown-content">
        <a href="/accounts/user-info/"><i class="fas fa-user"></i>Tài khoản</a>
        <a href="/accounts/user-info/order-history/"><i class="fas fa-shopping-bag"></i>Sản phẩm đã mua</a>
        <a href="/accounts/user-info/payment-history/"><i class="fas fa-wallet"></i>Lịch sử nạp tiền</a>
        <a href="/accounts/user-info/security/"><i class="fas fa-shield-alt"></i>Bảo mật</a>
        <a href="/accounts/user-info/wishlist/"><i class="fas fa-heart"></i>Sản phẩm yêu thích</a>
        <a href="/accounts/user-info/settings/"><i class="fas fa-cog"></i>Cài đặt</a>
        <a href="/accounts/user-info/referral/"><i class="fas fa-user-plus"></i>Giới thiệu bạn bè</a>
        <div class="dropdown-divider"></div>
        <a href="/accounts/logout/" class="text-danger"><i class="fas fa-sign-out-alt"></i>Đăng xuất</a>
    </div>
`;

// Định nghĩa các biến và hàm ở phạm vi toàn cục
window.SUPPORTED_LANGUAGES = {
    'vi': 'VI',
    'en': 'EN'
};

window.translationCache = new Map();

// Hàm dịch text
window.translateText = async function(text, targetLang) {
    const cacheKey = `${text}_${targetLang}`;
    if (translationCache.has(cacheKey)) {
        return translationCache.get(cacheKey);
    }

    try {
        // Lấy CSRF token từ form thay vì meta tag
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Kiểm tra text và target_lang trước khi gửi request
        if (!text || !targetLang) {
            throw new Error('Missing required parameters');
        }

        const response = await fetch('/accounts/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                text: text.trim(),
                target_lang: SUPPORTED_LANGUAGES[targetLang]
            })
        });

        if (!response.ok) {
            throw new Error(`Translation failed: ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            translationCache.set(cacheKey, data.translation);
            return data.translation;
        } else {
            throw new Error(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        throw error;
    }
};

// Hàm chuyển đổi ngôn ngữ
window.changeLanguage = async function(lang, showNotification) {
    if (!lang || !window.TRANSLATIONS[lang]) {
        console.error('Invalid language:', lang);
        return;
    }

    let loadingDialog;
    try {
        loadingDialog = Swal.fire({
            title: lang === 'en' ? 'Changing language...' : 'Đang chuyển đổi ngôn ngữ...',
            allowOutsideClick: false,
            showConfirmButton: false,
            willOpen: () => {
                Swal.showLoading();
            }
        });

        // 1. Cập nhật UI cho các nút ngôn ngữ
        document.querySelectorAll('.lang-btn').forEach(btn => {
            const isActive = btn.dataset.lang === lang;
            btn.classList.toggle('active', isActive);
            btn.style.background = isActive ? '#df2626' : 'transparent';
            btn.style.color = isActive ? 'white' : '#df2626';
            btn.style.borderColor = '#df2626';
        });

        // 2. Cập nhật nội dung tĩnh
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (window.TRANSLATIONS[lang][key]) {
                element.textContent = window.TRANSLATIONS[lang][key];
            }
        });

        // 3. Xử lý nội dung động
        if (lang === 'vi') {
            // Khôi phục text gốc
            document.querySelectorAll('[data-translate="true"]').forEach(element => {
                const originalText = element.getAttribute('data-original-text');
                if (originalText) {
                    element.textContent = originalText;
                }
            });
        } else {
            // Dịch nội dung động qua API
            const elements = Array.from(document.querySelectorAll('[data-translate="true"]'));
            const batchSize = 5; // Xử lý 5 phần tử một lần
            
            for (let i = 0; i < elements.length; i += batchSize) {
                const batch = elements.slice(i, i + batchSize);
                const promises = batch.map(async element => {
                    try {
                        const originalText = element.getAttribute('data-original-text') || element.textContent.trim();
                        if (!element.getAttribute('data-original-text')) {
                            element.setAttribute('data-original-text', originalText);
                        }
                        
                        const translatedText = await translateText(originalText, lang);
                        if (translatedText) {
                            element.textContent = translatedText;
                        }
                    } catch (error) {
                        console.error('Error translating element:', error);
                    }
                });
                
                await Promise.all(promises);
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }

        localStorage.setItem('selectedLanguage', lang);
        
        if (loadingDialog) {
            loadingDialog.close();
        }

        // Thông báo thành công
        const successMessage = lang === 'en' ? 
            'Language changed successfully' : 
            'Đã chuyển đổi ngôn ngữ thành công';
            
        if (showNotification) {
            await Swal.fire({
                icon: 'success',
                title: lang === 'en' ? 'Success!' : 'Thành công!',
                text: successMessage,
                timer: 1500,
                showConfirmButton: false
            });
        }

        // Thêm các placeholders
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            if (window.TRANSLATIONS[lang][key]) {
                element.placeholder = window.TRANSLATIONS[lang][key];
            }
        });

    } catch (error) {
        console.error('Error changing language:', error);
        
        if (loadingDialog) {
            loadingDialog.close();
        }

        const errorMessage = lang === 'en' ? 
            'Could not change language. Please try again later.' : 
            'Không thể chuyển đổi ngôn ngữ. Vui lòng thử lại sau.';

        if (showNotification) {
            await Swal.fire({
                icon: 'error',
                title: lang === 'en' ? 'Error!' : 'Lỗi!',
                text: errorMessage,
                confirmButtonText: lang === 'en' ? 'Close' : 'Đóng'
            });
        }
    }
};

// Hàm tự động thêm data-translate cho tất cả text tiếng Việt
function autoDetectVietnameseText() {
    const vietnameseRegex = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i;
    
    // Các thẻ và class cần bỏ qua
    const excludeTags = ['SCRIPT', 'STYLE', 'INPUT', 'TEXTAREA', 'CODE', 'PRE'];
    const excludeClasses = ['no-translate', 'code'];
    
    function shouldTranslate(node) {
        if (!node.parentElement) return true;
        
        // Kiểm tra các class loại trừ
        const hasExcludedClass = Array.from(node.parentElement.classList)
            .some(cls => excludeClasses.includes(cls));
        if (hasExcludedClass) return false;
        
        // Kiểm tra các thẻ loại trừ
        if (excludeTags.includes(node.parentElement.tagName)) return false;
        
        return true;
    }

    function walkText(node) {
        if (node.nodeType === 3) { // Text node
            const text = node.textContent.trim();
            if (text && vietnameseRegex.test(text) && shouldTranslate(node)) {
                const span = document.createElement('span');
                span.setAttribute('data-translate', 'true');
                span.textContent = text;
                node.parentNode.replaceChild(span, node);
            }
        } else if (node.nodeType === 1 && // Element node
                  !excludeTags.includes(node.tagName) && 
                  !node.hasAttribute('data-translate')) {
            // Chỉ xử lý các node con nếu node cha không có data-translate
            Array.from(node.childNodes).forEach(walkText);
        }
    }

    // Bắt đầu từ body
    walkText(document.body);
}

// Hàm cache sẵn tất cả text tiếng Việt
async function precacheVietnameseText() {
    const elements = document.querySelectorAll('[data-translate="true"]');
    const uniqueTexts = new Set();

    elements.forEach(el => {
        const text = el.textContent.trim();
        if (text) uniqueTexts.add(text);
    });

    try {
        const translations = await Promise.all(
            Array.from(uniqueTexts).map(text => translateText(text, 'en'))
        );
        console.log('Precached translations:', translations.length);
    } catch (error) {
        console.error('Error precaching translations:', error);
    }
}

// Khởi tạo khi trang load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Base.js loaded');
    
    // Khôi phục ngôn ngữ đã lưu mà không hiện thông báo
    const savedLang = localStorage.getItem('selectedLanguage') || 'vi';
    if (savedLang === 'en') {
        changeLanguage('en', false); // Không hiện thông báo khi tự động load
    }
    
    // Thêm event listener cho các nút ngôn ngữ
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const newLang = this.dataset.lang;
            const currentLang = localStorage.getItem('selectedLanguage') || 'vi';
            
            // Chỉ hiện thông báo khi thực sự thay đổi ngôn ngữ
            if (newLang !== currentLang) {
                changeLanguage(newLang, true);
            } else {
                changeLanguage(newLang, false);
            }
        });
    });
}); 