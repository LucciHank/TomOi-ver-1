document.addEventListener('DOMContentLoaded', function () {
    const categoriesSwiper = new Swiper('.categories-slider', {
        slidesPerView: 'auto',
        spaceBetween: 20,
        loop: true,
        loopedSlides: 10,
        watchSlidesProgress: true,
        observer: true,
        observeParents: true,
        navigation: {
            nextEl: '.nav-btn.next',
            prevEl: '.nav-btn.prev',
        },
        breakpoints: {
            320: {
                slidesPerView: 2,
                spaceBetween: 10
            },
            480: {
                slidesPerView: 3,
                spaceBetween: 15
            },
            768: {
                slidesPerView: 4,
                spaceBetween: 20
            }
        }
    });

    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            const productId = this.closest('.product-card').dataset.productId;
            addToCart(productId, event);
        });
    });

    // Load cart count khi trang web được tải
    loadCartItems();
    updateCartCount();
});

document.querySelectorAll('.add-to-cart-btn').forEach(button => {
    button.removeEventListener('click', function () { });
});

function formatPrice(price) {
    return parseFloat(price).toLocaleString('vi-VN') + 'đ';
}

function updateCartDropdown(cartItems) {
    try {
        const cartItemsContainer = document.querySelector('.cart-items');
        const emptyCartMessage = document.querySelector('.empty-cart');

        if (cartItemsContainer) {
            if (!cartItems || cartItems.length === 0) {
                if (emptyCartMessage) {
                    emptyCartMessage.style.display = 'block';
                }
                cartItemsContainer.innerHTML = '';
            } else {
                if (emptyCartMessage) {
                    emptyCartMessage.style.display = 'none';
                }

                cartItemsContainer.innerHTML = cartItems.map(item => `
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
            }

            // Cập nhật tổng tiền
            const totalAmount = document.querySelector('.total-amount');
            if (totalAmount && cartItems.length > 0) {
                const total = cartItems.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
                totalAmount.textContent = formatPrice(total);
            }
        }
    } catch (error) {
        console.error('Error updating cart dropdown:', error);
    }
}

function showConfirmation(message, onConfirm, onCancel) {
    const notification = document.createElement('div');
    notification.className = 'confirmation-dialog';
    notification.innerHTML = `
        <div class="confirmation-content">
            <div class="delete-icon">
                <i class="fas fa-times-circle"></i>
            </div>
            <p>${message}</p>
            <div class="confirmation-buttons">
                <button class="btn-confirm">Có</button>
                <button class="btn-cancel">Không</button>
            </div>
        </div>
    `;

    document.body.appendChild(notification);

    // Thêm animation khi hiển thị
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

function confirmRemoveItem(productId) {
    showConfirmation(
        'Bạn có chắc chắn muốn xóa sản phẩm này?',
        () => removeItem(productId),
        () => { } // Do nothing if cancelled
    );
}

function removeItem(productId) {
    fetch('/cart/remove/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ id: productId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Xóa item trực tiếp từ DOM
                const cartItem = document.querySelector(`.cart-item[data-id="${productId}"]`);
                if (cartItem) {
                    cartItem.remove();
                }

                // Kiểm tra nếu không còn sản phẩm nào
                const cartItems = document.querySelectorAll('.cart-item');
                if (cartItems.length === 0) {
                    const emptyCart = document.querySelector('.empty-cart');
                    if (emptyCart) {
                        emptyCart.style.display = 'block';
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
                const totalQuantity = data.cart_items.reduce((sum, item) => sum + item.quantity, 0);
                const cartCountBadge = document.querySelector('.cart-count-badge');
                if (cartCountBadge) {
                    cartCountBadge.textContent = totalQuantity;
                    cartCountBadge.style.display = totalQuantity > 0 ? 'flex' : 'none';
                }
            }
        });
}

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
                        // Chỉ cập nhật số lượng và tổng tiền, không cập nhật lại toàn bộ dropdown
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
                        const totalQuantity = data.cart_items.reduce((sum, item) => sum + item.quantity, 0);
                        const cartCountBadge = document.querySelector('.cart-count-badge');
                        if (cartCountBadge) {
                            cartCountBadge.textContent = totalQuantity;
                        }
                    }
                });
        });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    // Style cho notification
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 25px';
    notification.style.borderRadius = '5px';
    notification.style.backgroundColor = type === 'success' ? '#4CAF50' : '#f44336';
    notification.style.color = 'white';
    notification.style.zIndex = '9999';

    document.body.appendChild(notification);

    // Xóa notification sau 3 giây
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function addToCart(productId, event) {
    event.preventDefault();
    const btn = event.target.closest('button');
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    btn.disabled = true;

    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            id: productId,
            quantity: 1
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Load lại toàn bộ giỏ hàng để có thông tin đầy đủ
                fetch('/cart/api/')
                    .then(response => response.json())
                    .then(cartData => {
                        if (cartData.cart_items && cartData.cart_items.length > 0) {
                            const emptyCart = document.querySelector('.empty-cart');
                            if (emptyCart) {
                                emptyCart.style.display = 'none';
                            }
                            updateCartDropdown(cartData.cart_items);
                            updateCartCount();
                        }
                    });
                showNotification('Đã thêm vào giỏ hàng', 'success');
            } else {
                showNotification(data.error || 'Lỗi không xác định', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Không thể kết nối đến server', 'error');
        })
        .finally(() => {
            btn.disabled = false;
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

function updateCartCount() {
    fetch('/cart/count/')
        .then(response => response.json())
        .then(data => {
            const cartCountBadge = document.querySelector('.cart-count-badge');
            if (cartCountBadge) {
                cartCountBadge.textContent = data.count;
                // Ẩn badge nếu không có sản phẩm
                cartCountBadge.style.display = data.count > 0 ? 'flex' : 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}

function loadCartItems() {
    fetch('/cart/api/')
        .then(response => response.json())
        .then(data => {
            if (data.cart_items && data.cart_items.length > 0) {
                const emptyCart = document.querySelector('.empty-cart');
                if (emptyCart) {
                    emptyCart.style.display = 'none';
                }
                updateCartDropdown(data.cart_items);
                updateCartCount();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Gắn event listeners một lần duy nhất khi trang load
document.addEventListener('DOMContentLoaded', function () {
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
                    showConfirmation(
                        'Bạn có chắc chắn muốn xóa sản phẩm này?',
                        () => removeItem(productId),
                        () => { }
                    );
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

    // Event delegation cho input số lượng
    document.body.addEventListener('change', function (e) {
        if (e.target.classList.contains('quantity-input')) {
            const item = e.target.closest('.cart-item');
            if (!item) return;

            const productId = item.dataset.id;
            const maxStock = parseInt(item.dataset.stock);
            let value = parseInt(e.target.value);

            if (isNaN(value) || value < 1) value = 1;
            if (value > maxStock) {
                value = maxStock;
                showNotification('Đã điều chỉnh về số lượng tối đa có sẵn', 'warning');
            }

            e.target.value = value;
            updateQuantity(productId, value);
        }
    });

    loadCartItems();
    updateCartCount();
});