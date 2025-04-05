// Thêm vào đầu file
document.addEventListener('DOMContentLoaded', function () {
    // Load Font Awesome nếu chưa có
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(link);
    }

    loadCartItems();
    updateCartBadge();

    // Header Enhancements
    const mainNavbar = document.querySelector('.main-navbar');
    let lastScrollPosition = 0;
    let stickyHeaderClone;

    // Create a clone of the main navbar for sticky header
    function createStickyHeader() {
        stickyHeaderClone = mainNavbar.cloneNode(true);
        stickyHeaderClone.classList.add('sticky-header');
        document.body.appendChild(stickyHeaderClone);

        // Re-attach event listeners to the cloned elements
        attachDropdownListeners(stickyHeaderClone);

        // Setup search functionality in the clone
        setupSearch(stickyHeaderClone.querySelector('.search-form'));
    }

    createStickyHeader();

    // Handle scroll for sticky header
    window.addEventListener('scroll', function () {
        const currentScrollPosition = window.pageYOffset;

        // Show sticky header when scrolling up and we're past the header
        if (currentScrollPosition > 200 && currentScrollPosition < lastScrollPosition) {
            stickyHeaderClone.classList.add('show');
        } else {
            stickyHeaderClone.classList.remove('show');
        }

        lastScrollPosition = currentScrollPosition;
    });

    // Dropdown functionality
    function attachDropdownListeners(container) {
        // For touch devices - make first click show dropdown, second click follow link
        const dropdownTriggers = container.querySelectorAll('.navbar-action-item, .header-icon-link');

        dropdownTriggers.forEach(trigger => {
            let touchStarted = false;

            // Clear any existing listeners
            trigger.removeEventListener('touchstart', handleTouchStart);
            trigger.removeEventListener('touchend', handleTouchEnd);

            // Add new listeners
            trigger.addEventListener('touchstart', handleTouchStart);
            trigger.addEventListener('touchend', handleTouchEnd);

            function handleTouchStart() {
                touchStarted = true;
            }

            function handleTouchEnd(e) {
                if (!touchStarted) return;
                touchStarted = false;

                const dropdown = trigger.querySelector('.dropdown-content');
                if (!dropdown) return;

                // If dropdown is not visible, show it and prevent navigation
                if (!dropdown.classList.contains('show-dropdown')) {
                    e.preventDefault();

                    // Hide all other dropdowns
                    document.querySelectorAll('.dropdown-content').forEach(d => {
                        d.classList.remove('show-dropdown');
                    });

                    // Show this dropdown
                    dropdown.classList.add('show-dropdown');
                }
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.dropdown-content') && !e.target.closest('.navbar-action-item') && !e.target.closest('.header-icon-link')) {
                document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                    dropdown.classList.remove('show-dropdown');
                });
            }
        });
    }

    // Initial attachment to main navbar
    attachDropdownListeners(document);

    // Search suggestions functionality
    function setupSearch(searchForm) {
        if (!searchForm) return;

        const searchInput = searchForm.querySelector('.search-input');
        const suggestionsContainer = searchForm.querySelector('.search-suggestions');

        let debounceTimer;

        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);

            const query = this.value.trim();
            if (query.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(() => {
                // Fetch suggestions from the server
                fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.products && data.products.length > 0) {
                            displaySuggestions(data.products);
                        } else {
                            suggestionsContainer.innerHTML = `
                                <div class="no-suggestions">
                                    <p>Không tìm thấy sản phẩm phù hợp</p>
                                </div>
                            `;
                            suggestionsContainer.style.display = 'block';
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching search suggestions:', error);
                    });
            }, 300);
        });

        searchInput.addEventListener('focus', function () {
            if (this.value.trim().length >= 2) {
                suggestionsContainer.style.display = 'block';
            }
        });

        // Close suggestions when clicking outside
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.search-form')) {
                suggestionsContainer.style.display = 'none';
            }
        });

        function displaySuggestions(products) {
            let html = `
                <div class="suggestion-header">Sản phẩm gợi ý</div>
                <ul class="suggestion-list">
            `;

            products.slice(0, 5).forEach(product => {
                html += `
                    <li class="suggestion-item">
                        <a href="/products/${product.slug}/">
                            <div class="suggestion-product">
                                <img src="${product.image || '/static/images/placeholder.jpg'}" class="suggestion-image" alt="${product.name}">
                                <div class="suggestion-info">
                                    <div class="suggestion-name">${product.name}</div>
                                    <div class="suggestion-price">${formatPrice(product.price)}</div>
                                </div>
                            </div>
                        </a>
                    </li>
                `;
            });

            html += `
                </ul>
                <div class="suggestion-footer">
                    <a href="/search/?q=${encodeURIComponent(searchInput.value)}" class="view-all">Xem tất cả kết quả</a>
                </div>
            `;

            suggestionsContainer.innerHTML = html;
            suggestionsContainer.style.display = 'block';
        }
    }

    // Setup search on the main search form
    setupSearch(document.querySelector('.main-navbar .search-form'));

    // Helper function to format price
    function formatPrice(price) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND',
            minimumFractionDigits: 0
        }).format(price);
    }

    // Cart functionality
    function updateCart() {
        // Fetch cart data
        fetch('/api/cart/')
            .then(response => response.json())
            .then(data => {
                // Update cart count
                const cartCountElements = document.querySelectorAll('.cart-count');
                cartCountElements.forEach(element => {
                    element.textContent = data.total_items || 0;
                    element.style.display = data.total_items > 0 ? 'flex' : 'none';
                });

                // Update cart dropdown content
                const cartItems = document.querySelectorAll('.cart-items');
                cartItems.forEach(container => {
                    if (data.items && data.items.length > 0) {
                        let html = '';

                        data.items.forEach(item => {
                            html += `
                                <div class="cart-item" data-id="${item.id}">
                                    <div class="cart-item-details">
                                        <img src="${item.image || '/static/images/placeholder.jpg'}" class="cart-item-image" alt="${item.name}">
                                        <div class="cart-item-info">
                                            <div class="cart-item-name">${item.name}</div>
                                            <div class="cart-item-price">${formatPrice(item.price)} x ${item.quantity}</div>
                                        </div>
                                    </div>
                                    <button class="cart-item-remove" data-id="${item.id}">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            `;
                        });

                        container.innerHTML = html;

                        // Add event listeners for remove buttons
                        container.querySelectorAll('.cart-item-remove').forEach(button => {
                            button.addEventListener('click', function () {
                                const itemId = this.getAttribute('data-id');
                                removeFromCart(itemId);
                            });
                        });
                    } else {
                        container.innerHTML = `
                            <div class="empty-state">
                                <i class="fas fa-shopping-cart"></i>
                                <p>Giỏ hàng trống</p>
                            </div>
                        `;
                    }
                });

                // Update total amount
                const totalElements = document.querySelectorAll('.total-amount');
                totalElements.forEach(element => {
                    element.textContent = formatPrice(data.total_price || 0);
                });
            })
            .catch(error => {
                console.error('Error updating cart:', error);
            });
    }

    function removeFromCart(itemId) {
        fetch(`/api/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCart();
                }
            })
            .catch(error => {
                console.error('Error removing item from cart:', error);
            });
    }

    // Initial cart update
    updateCart();

    // Update cart periodically (every 30 seconds)
    setInterval(updateCart, 30000);
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
document.addEventListener('DOMContentLoaded', function () {
    loadCartItems();
    restoreCartBadge();

    // Lắng nghe sự kiện cartUpdated
    document.addEventListener('cartUpdated', function () {
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
window.translateText = async function (text, targetLang) {
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
document.addEventListener('DOMContentLoaded', function () {
    console.log('Base.js loaded');

    // Khôi phục ngôn ngữ đã lưu mà không hiện thông báo
    const savedLang = localStorage.getItem('selectedLanguage') || 'vi';
    if (savedLang === 'en') {
        changeLanguage('en'); // Không hiện thông báo khi tự động load
    }

    // Thêm event listener cho các nút ngôn ngữ
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function () {
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

    // Thêm hàm xử lý search suggestions
    setupSearchSuggestions();
});

// Cập nhật hàm thiết lập chức năng gợi ý tìm kiếm để sửa lỗi modal không hiện
function setupSearchSuggestions() {
    const searchForms = document.querySelectorAll('.search-form');

    searchForms.forEach(form => {
        const searchInput = form.querySelector('.search-input');
        const suggestionsContainer = form.querySelector('.search-suggestions');
        const searchResultsList = form.querySelector('.result-list');
        const noSuggestionsDiv = form.querySelector('.no-suggestions');
        const searchHistoryList = form.querySelector('.search-history .suggestion-list');

        if (!searchInput || !suggestionsContainer) return;

        console.log("Setup search form with input:", searchInput);

        // Hiển thị gợi ý khi click vào search input
        searchInput.addEventListener('click', function (e) {
            console.log("Search input clicked, displaying suggestions");

            // Hiển thị container gợi ý - sửa lỗi không hiện bằng cách thêm inline style trực tiếp
            suggestionsContainer.style.display = 'block';

            // Debug để kiểm tra trạng thái hiển thị
            console.log("Suggestions container display:", suggestionsContainer.style.display);
            console.log("Suggestions container visibility:", getComputedStyle(suggestionsContainer).visibility);
            console.log("Suggestions container dimensions:", suggestionsContainer.offsetWidth, "x", suggestionsContainer.offsetHeight);

            // Load lịch sử tìm kiếm
            loadSearchHistory(searchHistoryList);

            // Nếu đã có text trong input, tìm kiếm luôn
            if (this.value.trim().length >= 1) {
                searchProducts(this.value.trim(), searchResultsList, noSuggestionsDiv);
            }

            // Ngăn sự kiện click lan tỏa để tránh bị đóng
            e.stopPropagation();
        });

        // Hiển thị gợi ý khi focus vào input để đảm bảo hiển thị trong mọi trường hợp
        searchInput.addEventListener('focus', function (e) {
            console.log("Search input focused, displaying suggestions");
            suggestionsContainer.style.display = 'block';

            // Load lịch sử tìm kiếm ngay khi focus
            loadSearchHistory(searchHistoryList);

            if (this.value.trim().length >= 1) {
                searchProducts(this.value.trim(), searchResultsList, noSuggestionsDiv);
            }
        });

        // Đóng gợi ý khi click ra ngoài
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.search-form')) {
                suggestionsContainer.style.display = 'none';
            }
        });

        // Xử lý khi gõ vào ô tìm kiếm
        let debounceTimer;
        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);

            const query = this.value.trim();

            // Hiển thị container gợi ý
            suggestionsContainer.style.display = 'block';

            if (query.length >= 1) {
                debounceTimer = setTimeout(() => {
                    searchProducts(query, searchResultsList, noSuggestionsDiv);
                }, 300);
            } else {
                // Ẩn phần kết quả nếu không có query
                searchResultsList.parentElement.style.display = 'none';
                noSuggestionsDiv.style.display = 'none';
            }
        });

        // Xử lý khi submit form tìm kiếm
        form.addEventListener('submit', function (e) {
            const query = searchInput.value.trim();
            if (query) {
                // Lưu vào lịch sử tìm kiếm
                saveSearchHistory(query);
            }
        });
    });
}

// Sau khi DOM đã sẵn sàng, gọi hàm thiết lập
document.addEventListener('DOMContentLoaded', function () {
    // Gọi chức năng thiết lập search suggestions
    console.log("DOM loaded, setting up search suggestions");
    setupSearchSuggestions();

    // Thêm kiểm tra để đảm bảo modal hiển thị sau khi trang đã load hoàn toàn
    window.addEventListener('load', function () {
        console.log("Window fully loaded, ensuring search suggestions are working");

        // Kiểm tra lại modal sau khi trang đã load hoàn toàn
        document.querySelectorAll('.search-input').forEach(input => {
            input.addEventListener('click', function (e) {
                const suggestionsContainer = this.closest('.search-form').querySelector('.search-suggestions');
                if (suggestionsContainer) {
                    console.log("Ensuring suggestions container is displayed on click after load");
                    suggestionsContainer.style.display = 'block';
                    e.stopPropagation();
                }
            });
        });
    });
});

// Hàm tìm kiếm sản phẩm theo từ khóa
function searchProducts(query, resultsList, noSuggestionsDiv) {
    // Hiển thị phần kết quả tìm kiếm
    resultsList.parentElement.style.display = 'block';

    // Gọi API tìm kiếm sản phẩm
    fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.products && data.products.length > 0) {
                // Hiển thị kết quả
                displaySearchResults(data.products, resultsList);
                noSuggestionsDiv.style.display = 'none';
            } else {
                // Hiển thị không có kết quả
                resultsList.innerHTML = '';
                resultsList.parentElement.style.display = 'none';
                noSuggestionsDiv.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            resultsList.innerHTML = '';
            resultsList.parentElement.style.display = 'none';
            noSuggestionsDiv.style.display = 'block';
        });
}

// Hiển thị kết quả tìm kiếm
function displaySearchResults(products, resultsList) {
    let html = '';

    products.slice(0, 5).forEach(product => {
        html += `
            <li class="suggestion-item" style="padding: 8px 15px; border-bottom: 1px solid #f4f4f4;">
                <a href="/products/${product.slug}/" style="text-decoration: none; color: #333; display: block;">
                    <div class="suggestion-product" style="display: flex; align-items: center;">
                        <img src="${product.image || '/static/images/placeholder.jpg'}" 
                            class="suggestion-image" 
                            alt="${product.name}"
                            style="width: 40px; height: 40px; object-fit: cover; margin-right: 10px;">
                        <div class="suggestion-info" style="flex: 1;">
                            <div class="suggestion-name" style="font-size: 14px; margin-bottom: 3px;">${product.name}</div>
                            <div class="suggestion-price" style="font-size: 13px; color: #c72020; font-weight: 600;">${formatPrice(product.price)}</div>
                        </div>
                    </div>
                </a>
            </li>
        `;
    });

    resultsList.innerHTML = html;
}

// Lưu lịch sử tìm kiếm
function saveSearchHistory(query) {
    // Lấy lịch sử tìm kiếm hiện tại
    let searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');

    // Kiểm tra xem đã có query này trong lịch sử chưa
    const index = searchHistory.indexOf(query);
    if (index !== -1) {
        // Nếu có rồi, xóa để thêm lại vào đầu
        searchHistory.splice(index, 1);
    }

    // Thêm query mới vào đầu mảng
    searchHistory.unshift(query);

    // Giới hạn số lượng lịch sử
    if (searchHistory.length > 5) {
        searchHistory = searchHistory.slice(0, 5);
    }

    // Lưu lại vào localStorage
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
}

// Tải lịch sử tìm kiếm
function loadSearchHistory(historyList) {
    // Nếu không có historyList, thoát
    if (!historyList) return;

    // Lấy lịch sử tìm kiếm từ localStorage
    const searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');

    // Nếu không có lịch sử, ẩn phần lịch sử
    if (searchHistory.length === 0) {
        historyList.parentElement.style.display = 'none';
        return;
    }

    // Hiển thị phần lịch sử
    historyList.parentElement.style.display = 'block';

    // Tạo HTML cho lịch sử tìm kiếm
    let html = '';

    searchHistory.forEach(query => {
        html += `
            <li class="suggestion-item" style="padding: 8px 15px; border-bottom: 1px solid #f4f4f4; display: flex; justify-content: space-between;">
                <a href="/search?q=${encodeURIComponent(query)}" style="text-decoration: none; color: #333; display: block; flex: 1;">
                    <i class="fas fa-history" style="margin-right: 10px; color: #888;"></i>
                    <span>${query}</span>
                </a>
                <button class="clear-history-item" data-query="${query}" style="background: none; border: none; color: #888; cursor: pointer; font-size: 12px;">
                    <i class="fas fa-times"></i>
                </button>
            </li>
        `;
    });

    historyList.innerHTML = html;

    // Thêm sự kiện xóa cho từng mục lịch sử
    historyList.querySelectorAll('.clear-history-item').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const query = this.getAttribute('data-query');
            removeFromSearchHistory(query);

            // Reload lịch sử
            loadSearchHistory(historyList);
        });
    });
}

// Xóa một mục khỏi lịch sử tìm kiếm
function removeFromSearchHistory(query) {
    // Lấy lịch sử tìm kiếm hiện tại
    let searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');

    // Lọc bỏ query cần xóa
    searchHistory = searchHistory.filter(item => item !== query);

    // Lưu lại vào localStorage
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
}

// Xóa toàn bộ lịch sử tìm kiếm
function clearSearchHistory() {
    localStorage.removeItem('searchHistory');
}

// Functions to handle hover on dropdown elements
document.addEventListener('DOMContentLoaded', function () {
    // Add hover functionality for header dropdowns
    const headerIconLinks = document.querySelectorAll('.header-icon-link');
    headerIconLinks.forEach(link => {
        link.addEventListener('mouseenter', function () {
            this.querySelector('.dropdown-content').style.display = 'block';
        });
        link.addEventListener('mouseleave', function () {
            this.querySelector('.dropdown-content').style.display = 'none';
        });
    });

    // Add hover functionality for navbar action dropdowns
    const navbarActionItems = document.querySelectorAll('.navbar-action-item');
    navbarActionItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            this.querySelector('.dropdown-content').style.display = 'block';
        });
        item.addEventListener('mouseleave', function () {
            this.querySelector('.dropdown-content').style.display = 'none';
        });
    });

    // Add hover effect for search button
    const searchButtons = document.querySelectorAll('.search-button');
    searchButtons.forEach(button => {
        button.addEventListener('mouseenter', function () {
            this.style.background = '#d32f2f';
            this.style.color = 'white';
        });
        button.addEventListener('mouseleave', function () {
            this.style.background = '#ffe9e9';
            this.style.color = '#d32f2f';
        });
    });
});

// Thêm xử lý dropdown header khi hover hoặc click
document.addEventListener('DOMContentLoaded', function () {
    // Xử lý dropdown header (thông báo, tin nhắn)
    const headerDropdowns = document.querySelectorAll('.header-icon-link');

    headerDropdowns.forEach(dropdown => {
        const dropdownContent = dropdown.querySelector('.dropdown-content');
        if (!dropdownContent) return;

        // Hiển thị dropdown khi hover
        dropdown.addEventListener('mouseenter', function () {
            closeAllDropdowns();
            dropdownContent.style.display = 'block';
        });

        // Ẩn dropdown khi mouse leave
        dropdown.addEventListener('mouseleave', function () {
            setTimeout(() => {
                if (!dropdown.matches(':hover')) {
                    dropdownContent.style.display = 'none';
                }
            }, 200);
        });

        // Hiển thị/ẩn dropdown khi click
        dropdown.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            } else {
                closeAllDropdowns();
                dropdownContent.style.display = 'block';
            }
        });
    });

    // Đóng tất cả dropdown khi click bên ngoài
    document.addEventListener('click', function () {
        closeAllDropdowns();
    });

    // Hàm đóng tất cả dropdown
    function closeAllDropdowns() {
        document.querySelectorAll('.dropdown-content').forEach(content => {
            if (content.closest('.navbar-action-item') && !content.closest('.header-icon-link')) {
                // Không đóng dropdown trong navbar-action-item (giỏ hàng, user)
                return;
            }
            content.style.display = 'none';
        });
    }

    // Gọi chức năng thiết lập search suggestions
    console.log("DOM loaded, setting up search suggestions");
    setupSearchSuggestions();

    // Thêm kiểm tra để đảm bảo modal hiển thị sau khi trang đã load hoàn toàn
    window.addEventListener('load', function () {
        console.log("Window fully loaded, ensuring search suggestions are working");

        // Kiểm tra lại modal sau khi trang đã load hoàn toàn
        document.querySelectorAll('.search-input').forEach(input => {
            input.addEventListener('click', function (e) {
                const suggestionsContainer = this.closest('.search-form').querySelector('.search-suggestions');
                if (suggestionsContainer) {
                    console.log("Ensuring suggestions container is displayed on click after load");
                    suggestionsContainer.style.display = 'block';
                    e.stopPropagation();
                }
            });
        });
    });
}); 