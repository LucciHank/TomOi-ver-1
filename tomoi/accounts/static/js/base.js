// Thêm vào đầu file
document.addEventListener('DOMContentLoaded', function() {
    // Load Font Awesome nếu chưa có
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(link);
    }
    
    loadCartItems();
    updateCartBadge();
});

// Cập nhật hàm updateCartDropdown để hiển thị thêm thông tin variant
function updateCartDropdown(cartItems) {
    const cartItemsContainer = document.querySelector('.cart-items');
    const emptyCart = document.querySelector('.empty-cart');
    const totalAmount = document.querySelector('.total-amount');
    const cartCountBadge = document.querySelector('.cart-count-badge');

    console.log('Updating cart with items:', cartItems);

    if (!cartItems || cartItems.length === 0) {
        if (emptyCart) emptyCart.style.display = 'block';
        if (cartItemsContainer) cartItemsContainer.innerHTML = '';
        if (totalAmount) totalAmount.textContent = '0đ';
        updateCartBadge(0);
        return;
    }

    if (emptyCart) emptyCart.style.display = 'none';
    
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = cartItems.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <div class="item-image">
                    <img src="${item.image || '/static/images/placeholder.png'}" alt="${item.name}">
                </div>
                <div class="item-content">
                    <div class="item-info">
                        <h6 class="item-name">${item.name}</h6>
                        <div class="item-price">${formatPrice(item.price)}</div>
                    </div>
                    <div class="item-controls">
                        <div class="quantity-controls">
                            <button type="button" class="btn btn-sm btn-outline-secondary minus-btn">
                                <i class="fas fa-minus"></i>
                            </button>
                            <span class="quantity mx-2">${item.quantity}</span>
                            <button type="button" class="btn btn-sm btn-outline-secondary plus-btn">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                        <button type="button" class="btn btn-sm btn-outline-danger remove-btn">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        // Thêm event listeners cho các nút
        cartItemsContainer.querySelectorAll('.cart-item').forEach(item => {
            const itemId = item.dataset.id;
            const minusBtn = item.querySelector('.minus-btn');
            const plusBtn = item.querySelector('.plus-btn');
            const removeBtn = item.querySelector('.remove-btn');
            const quantitySpan = item.querySelector('.quantity');

            minusBtn.addEventListener('click', () => {
                const newQty = parseInt(quantitySpan.textContent) - 1;
                if (newQty >= 1) {
                    updateCartItemQuantity(itemId, newQty);
                } else {
                    removeCartItem(itemId);
                }
            });

            plusBtn.addEventListener('click', () => {
                const newQty = parseInt(quantitySpan.textContent) + 1;
                updateCartItemQuantity(itemId, newQty);
            });

            removeBtn.addEventListener('click', () => {
                removeCartItem(itemId);
            });
        });

        // Cập nhật tổng tiền
        const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        if (totalAmount) totalAmount.textContent = formatPrice(total);

        // Cập nhật badge
        const totalQuantity = cartItems.reduce((sum, item) => sum + item.quantity, 0);
        updateCartBadge(totalQuantity);
    }
}

// Thêm hàm cập nhật badge
function updateCartBadge(count) {
    const badge = document.querySelector('.cart-count-badge');
    if (badge) {
        if (count && count > 0) {
            badge.style.display = 'block';
            badge.textContent = count;
            localStorage.setItem('cartCount', count);
        } else {
            badge.style.display = 'none';
            badge.textContent = '0';
            localStorage.removeItem('cartCount');
        }
    }
}

// Thêm hàm khôi phục badge từ localStorage
function restoreCartBadge() {
    const count = localStorage.getItem('cartCount');
    if (count) {
        updateCartBadge(parseInt(count));
    }
}

// Thêm các hàm xử lý cập nhật và xóa
async function updateCartItemQuantity(itemId, newQuantity) {
    if (newQuantity < 1) {
        removeCartItem(itemId);
        return;
    }
    
    try {
        const response = await fetch(API_ENDPOINTS.CART_UPDATE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: newQuantity,
                action: 'update'
            })
        });

        const data = await response.json();
        if (data.success) {
            updateCartDropdown(data.cart_items);
            updateCartBadge(data.total_items);
        } else {
            throw new Error(data.message || 'Có lỗi xảy ra khi cập nhật giỏ hàng');
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            text: error.message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    }
}

async function removeCartItem(itemId) {
    try {
        const response = await fetch('/store/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                item_id: itemId
            })
        });

        const data = await response.json();
        if (data.success) {
            updateCartDropdown(data.cart_items);
        } else {
            throw new Error(data.message || 'Có lỗi xảy ra khi xóa sản phẩm');
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            text: error.message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    }
}

// Hàm format giá tiền
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price).replace('₫', 'đ');
}

// Load giỏ hàng khi trang tải xong
document.addEventListener('DOMContentLoaded', function() {
    loadCartItems();
    restoreCartBadge();
    
    // Lắng nghe sự kiện cartUpdated
    document.addEventListener('cartUpdated', function() {
        loadCartItems();
    });
});

// Sửa lại các URL endpoint
const API_ENDPOINTS = {
    CART_API: '/store/cart/api/',
    CART_ADD: '/store/cart/add/',
    CART_UPDATE: '/store/cart/update/',
    CART_REMOVE: '/store/cart/remove/',
    GET_PRICE: '/store/api/get-price/'
};

// Hàm load giỏ hàng
async function loadCartItems() {
    try {
        const response = await fetch(API_ENDPOINTS.CART_API);
        const data = await response.json();
        console.log('Cart data:', data);

        if (data.cart_items && Array.isArray(data.cart_items)) {
            updateCartDropdown(data.cart_items);
        } else {
            console.error('Invalid cart data format:', data);
        }
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

// Hàm thêm vào giỏ hàng
async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch(API_ENDPOINTS.CART_ADD, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });

        const data = await response.json();
        if (data.success) {
            updateCartDropdown(data.cart_items);
            Swal.fire({
                icon: 'success',
                text: 'Đã thêm vào giỏ hàng',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            text: 'Có lỗi xảy ra, vui lòng thử lại',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    }
}

// Hàm cập nhật giá
async function updatePrice(variantId, duration) {
    try {
        const response = await fetch(`${API_ENDPOINTS.GET_PRICE}?variant_id=${variantId}&duration=${duration}`);
        const data = await response.json();
        if (data.success) {
            document.querySelector('.current-price').textContent = formatPrice(data.price);
        }
    } catch (error) {
        console.error('Error fetching price:', error);
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
        changeLanguage('en'); // Không hiện thông báo khi tự động load
    }
    
    // Thêm event listener cho các nút ngôn ngữ
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const newLang = this.dataset.lang;
            const currentLang = localStorage.getItem('selectedLanguage') || 'vi';
            
            // Chỉ hiện thông báo khi thực sự thay đổi ngôn ngữ
            if (newLang !== currentLang) {
                changeLanguage(newLang);
            } else {
                changeLanguage(newLang);
            }
        });
    });

    // Khôi phục ngôn ngữ đã chọn khi tải trang
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === savedLang);
    });
}); 