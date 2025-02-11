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