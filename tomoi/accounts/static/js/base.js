// Lưu ngôn ngữ hiện tại vào localStorage
const currentLang = "{{ LANGUAGE_CODE }}";
localStorage.setItem('language', currentLang);

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

function updateDropdownQuantity(itemId, change) {
    const dropdownItem = document.querySelector(`.cart-dropdown-item[data-id="${itemId}"]`);
    if (!dropdownItem) return;

    const quantityInput = dropdownItem.querySelector('.quantity-input');
    const currentQuantity = parseInt(quantityInput.value);
    const maxStock = parseInt(dropdownItem.dataset.stock);

    let newQuantity = currentQuantity + change;

    if (newQuantity < 1 || newQuantity > maxStock) return;

    // Cập nhật giao diện ngay
    quantityInput.value = newQuantity;

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: newQuantity
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Cập nhật tổng tiền trong dropdown
                const totalElement = document.querySelector('.cart-dropdown-total');
                if (totalElement) {
                    totalElement.textContent = data.total_amount;
                }

                // Cập nhật số lượng trong header
                const cartCount = document.querySelector('.cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                }

                // Cập nhật cả cart.html nếu đang mở
                const cartPage = document.querySelector('.cart-page');
                if (cartPage) {
                    const cartItem = cartPage.querySelector(`.cart-item-card[data-id="${itemId}"]`);
                    if (cartItem) {
                        cartItem.querySelector('.quantity-input').value = newQuantity;
                        // Cập nhật tổng tiền trong cart page
                        document.querySelector('.summary-row:nth-child(1) span:last-child').textContent = data.total_amount;
                        document.querySelector('.summary-row:nth-child(2) span:last-child').textContent = data.discount_amount;
                        document.querySelector('.total-row span:last-child').textContent = data.final_amount;
                    }
                }
            }
        });
}

function removeItem(itemId) {
    fetch('/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Xóa item khỏi dropdown
                const dropdownItem = document.querySelector(`.cart-dropdown-item[data-id="${itemId}"]`);
                if (dropdownItem) {
                    dropdownItem.remove();
                }

                // Xóa item khỏi cart page nếu đang mở
                const cartItem = document.querySelector(`.cart-item-card[data-id="${itemId}"]`);
                if (cartItem) {
                    cartItem.remove();
                }

                // Cập nhật số lượng trong header
                const cartCount = document.querySelector('.cart-count');
                if (cartCount) {
                    cartCount.textContent = data.count;
                }

                // Cập nhật tổng tiền trong dropdown
                const dropdownTotal = document.querySelector('.cart-dropdown-total');
                if (dropdownTotal) {
                    dropdownTotal.textContent = data.total_amount;
                }

                // Cập nhật tổng tiền trong cart page nếu đang mở
                const cartPage = document.querySelector('.cart-page');
                if (cartPage) {
                    document.querySelector('.summary-row:nth-child(1) span:last-child').textContent = data.total_amount;
                    document.querySelector('.summary-row:nth-child(2) span:last-child').textContent = data.discount_amount;
                    document.querySelector('.total-row span:last-child').textContent = data.final_amount;
                }

                // Reload nếu giỏ hàng trống
                if (data.count === 0) {
                    location.reload();
                }
            }
        });
}

// Event listeners khi trang load xong
document.addEventListener('DOMContentLoaded', function () {
    // Event listeners cho nút tăng/giảm trong dropdown
    document.querySelectorAll('.cart-dropdown .btn-quantity').forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation(); // Ngăn dropdown đóng lại
            const itemId = this.closest('.cart-dropdown-item').dataset.id;
            const change = this.classList.contains('plus') ? 1 : -1;
            updateDropdownQuantity(itemId, change);
        });
    });

    // Event listeners cho nút xóa trong dropdown
    document.querySelectorAll('.cart-dropdown .btn-remove').forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation(); // Ngăn dropdown đóng lại
            const itemId = this.closest('.cart-dropdown-item').dataset.id;
            if (confirm('Bạn có chắc muốn xóa sản phẩm này?')) {
                removeItem(itemId);
            }
        });
    });
});

function changeLanguage(lang) {
    var select = document.querySelector('.goog-te-combo');
    if (select) {
        select.value = lang;
        select.dispatchEvent(new Event('change'));
    }
}

// Thêm event listener cho cart hover
document.addEventListener('DOMContentLoaded', function () {
    const cartWrapper = document.querySelector('.cart-wrapper');
    if (cartWrapper) {
        cartWrapper.addEventListener('mouseenter', function () {
            fetch('/cart/api/')
                .then(response => response.json())
                .then(data => {
                    if (data.cart_items && data.cart_items.length > 0) {
                        const cartItemsContainer = document.querySelector('.cart-items');
                        const emptyCart = document.querySelector('.empty-cart');

                        if (emptyCart) {
                            emptyCart.style.display = 'none';
                        }

                        if (cartItemsContainer) {
                            cartItemsContainer.innerHTML = data.cart_items.map(item => `
                                <div class="cart-item" data-id="${item.id}" data-stock="${item.stock}">
                                    <div class="item-image">
                                        <img src="${item.image || '/static/images/placeholder.png'}" alt="${item.name}">
                                    </div>
                                    <div class="item-content">
                                        <div class="item-info">
                                            <h6 class="item-name">${item.name}</h6>
                                            <div class="item-price">
                                                <span class="new-price">${formatPrice(item.price)}</span>
                                                ${item.old_price ? `
                                                    <span class="old-price">${formatPrice(item.old_price)}</span>
                                                    <span class="discount-badge">-${item.discount}%</span>
                                                ` : ''}
                                            </div>
                                        </div>
                                        <div class="item-controls">
                                            <div class="quantity-controls">
                                                <button class="btn-quantity minus">-</button>
                                                <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="${item.stock}">
                                                <button class="btn-quantity plus">+</button>
                                            </div>
                                            <button class="btn-remove" onclick="confirmRemoveItem(${item.id})">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            `).join('');

                            // Cập nhật tổng tiền
                            const totalAmount = document.querySelector('.total-amount');
                            if (totalAmount) {
                                const total = data.cart_items.reduce((sum, item) =>
                                    sum + (parseFloat(item.price) * item.quantity), 0
                                );
                                totalAmount.textContent = formatPrice(total);
                            }

                            // Gắn lại event listeners cho các nút điều khiển
                            setupCartControls();
                        }
                    }
                });
        });
    }
});

// Hàm format giá tiền
function formatPrice(price) {
    return parseFloat(price).toLocaleString('vi-VN') + 'đ';
}

// Hàm setup các controls trong giỏ hàng
function setupCartControls() {
    // Event delegation cho nút tăng/giảm số lượng
    document.body.addEventListener('click', function (e) {
        if (e.target.classList.contains('minus') || e.target.classList.contains('plus')) {
            const item = e.target.closest('.cart-item');
            if (!item) return;

            const input = item.querySelector('.quantity-input');
            const productId = item.dataset.id;
            const maxStock = parseInt(item.dataset.stock);
            const currentQty = parseInt(input.value);

            if (e.target.classList.contains('minus')) {
                if (currentQty === 1) {
                    confirmRemoveItem(productId);
                } else {
                    updateQuantity(productId, currentQty - 1);
                }
            } else {
                if (currentQty >= maxStock) {
                    showNotification('Vượt quá số lượng sản phẩm còn lại', 'error');
                    return;
                }
                updateQuantity(productId, currentQty + 1);
            }
        }
    });
}

// Các hàm cần thiết cho giỏ hàng
function updateQuantity(productId, quantity) {
    fetch(`/cart/check-stock/${productId}/`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.stock < quantity) {
                showNotification('Vượt quá số lượng tài khoản có sẵn', 'error');
                return;
            }

            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ id: productId, quantity: quantity })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Cập nhật UI
                        const cartItem = document.querySelector(`.cart-item[data-id="${productId}"]`);
                        if (cartItem) {
                            const quantityInput = cartItem.querySelector('.quantity-input');
                            if (quantityInput) {
                                quantityInput.value = quantity;
                            }
                        }

                        // Cập nhật tổng tiền
                        const totalAmount = document.querySelector('.total-amount');
                        if (totalAmount) {
                            const total = data.cart_items.reduce((sum, item) =>
                                sum + (parseFloat(item.price) * item.quantity), 0
                            );
                            totalAmount.textContent = formatPrice(total);
                        }

                        // Cập nhật badge
                        const cartCountBadge = document.querySelector('.cart-count-badge');
                        if (cartCountBadge) {
                            const totalQuantity = data.cart_items.reduce((sum, item) => sum + item.quantity, 0);
                            cartCountBadge.textContent = totalQuantity;
                        }
                    }
                });
        });
}

function confirmRemoveItem(productId) {
    showConfirmation(
        'Bạn có chắc chắn muốn xóa sản phẩm này?',
        () => removeItem(productId),
        () => { }
    );
}

function showConfirmation(message, onConfirm, onCancel) {
    const notification = document.createElement('div');
    notification.className = 'confirmation-dialog';
    notification.innerHTML = `
        <div class="confirmation-content">
            <div class="delete-icon">
                <i class="far fa-times-circle"></i>
            </div>
            <p>${message}</p>
            <div class="confirmation-buttons">
                <button class="btn-confirm">Có</button>
                <button class="btn-cancel">Không</button>
            </div>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.querySelector('.confirmation-content').style.transform = 'scale(1)';
        notification.querySelector('.confirmation-content').style.opacity = '1';
    }, 10);

    const confirmBtn = notification.querySelector('.btn-confirm');
    const cancelBtn = notification.querySelector('.btn-cancel');

    confirmBtn.addEventListener('click', () => {
        onConfirm();
        notification.remove();
    });

    cancelBtn.addEventListener('click', () => {
        onCancel();
        notification.remove();
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 25px';
    notification.style.borderRadius = '5px';
    notification.style.backgroundColor = type === 'success' ? '#4CAF50' : '#f44336';
    notification.style.color = 'white';
    notification.style.zIndex = '9999';

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}