console.log('Base.js loaded');

function removeItem(productId) {
    Swal.fire({
        title: 'Xác nhận xóa',
        text: 'Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
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
                    // Xóa item khỏi dropdown
                    const dropdownItem = document.querySelector(`.cart-dropdown-content .cart-item[data-id="${productId}"]`);
                    if (dropdownItem) {
                        dropdownItem.remove();
                    }

                    // Xóa item khỏi trang cart nếu đang ở trang đó
                    const cartPageItem = document.querySelector(`.cart-page .cart-item[data-id="${productId}"]`);
                    if (cartPageItem) {
                        cartPageItem.remove();
                    }

                    // Cập nhật tổng tiền
                    updateTotalAmount();

                    // Kiểm tra nếu giỏ hàng trống
                    const cartItems = document.querySelectorAll('.cart-item');
                    if (cartItems.length === 0) {
                        const emptyCart = document.querySelector('.empty-cart');
                        if (emptyCart) emptyCart.style.display = 'block';
                        
                        // Nếu đang ở trang cart, hiển thị thông báo giỏ hàng trống
                        const cartPage = document.querySelector('.cart-page');
                        if (cartPage) {
                            cartPage.innerHTML = `
                                <div class="empty-cart-message">
                                    <i class="fas fa-shopping-cart"></i>
                                    <p>Giỏ hàng của bạn đang trống</p>
                                    <a href="/" class="btn btn-primary">Tiếp tục mua sắm</a>
                                </div>
                            `;
                        }
                    }

                    // Cập nhật số lượng badge
                    updateCartCount(data.total_items);

                    Swal.fire({
                        title: 'Đã xóa!',
                        text: 'Sản phẩm đã được xóa khỏi giỏ hàng',
                        icon: 'success',
                        timer: 1500,
                        showConfirmButton: false
                    });
                } else {
                    Swal.fire({
                        title: 'Lỗi!',
                        text: data.error || 'Có lỗi xảy ra',
                        icon: 'error'
                    });
                }
            })
            .catch(error => {
                console.error('Remove error:', error);
                Swal.fire({
                    title: 'Lỗi!',
                    text: 'Không thể kết nối đến server',
                    icon: 'error'
                });
            });
        }
    });
}

function loadCartItems() {
    console.log('Loading cart items...');
    fetch('/cart/api/')
        .then(response => {
            console.log('Response status:', response.status);  // Debug log
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Cart data received:', data);  // Debug log
            if (data.cart_items && data.cart_items.length > 0) {
                updateCartDropdown(data.cart_items);
            } else {
                // Hiển thị giỏ hàng trống
                const cartItemsContainer = document.querySelector('.cart-items');
                const emptyCart = document.querySelector('.empty-cart');
                if (cartItemsContainer) cartItemsContainer.innerHTML = '';
                if (emptyCart) emptyCart.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error loading cart:', error);
            // Hiển thị giỏ hàng trống khi có lỗi
            const cartItemsContainer = document.querySelector('.cart-items');
            const emptyCart = document.querySelector('.empty-cart');
            if (cartItemsContainer) cartItemsContainer.innerHTML = '';
            if (emptyCart) emptyCart.style.display = 'block';
        });
}

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

function formatPrice(value) {
    if (isNaN(value) || value === null) {
        console.log('Invalid price value:', value);
        return '0đ';
    }
    return Math.round(value).toLocaleString('vi-VN') + 'đ';
}

function showNotification(message, type = 'success') {
    Swal.fire({
        title: type === 'success' ? 'Thành công!' : 'Lỗi!',
        text: message,
        icon: type,
        timer: 2000,
        showConfirmButton: false
    });
}

// Đảm bảo loadCartItems được gọi khi trang tải xong
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, loading cart...');
    loadCartItems();

    // Thêm event listener cho nút + và -
    document.body.addEventListener('click', function(e) {
        console.log('Click event:', e.target);
        
        // Xử lý nút tăng/giảm số lượng
        if (e.target.matches('.quantity-btn')) {
            console.log('Quantity button clicked');
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const input = cartItem.querySelector('.quantity-input');
            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let currentQty = parseInt(input.value);
            const price = parseFloat(cartItem.dataset.price);

            console.log('Before update:', { currentQty, maxStock, price });

            if (e.target.classList.contains('minus')) {
                if (currentQty <= 1) {
                    if (confirm('Bạn có muốn xóa sản phẩm này?')) {
                        removeItem(productId);
                    }
                    return;
                }
                currentQty--;
            } else if (e.target.classList.contains('plus')) {
                if (currentQty >= maxStock) {
                    Swal.fire({
                        title: 'Thông báo',
                        text: 'Vượt quá số lượng trong kho',
                        icon: 'warning'
                    });
                    return;
                }
                currentQty++;
            }

            // Cập nhật UI ngay lập tức
            input.value = currentQty;

            // Cập nhật giá tiền của item
            const itemTotal = price * currentQty;
            const currentPriceElement = cartItem.querySelector('.current-price');
            if (currentPriceElement) {
                currentPriceElement.textContent = formatPrice(itemTotal);
            }

            // Cập nhật tổng tiền
            updateTotalAmount();

            // Gửi request cập nhật lên server
            updateCartItem(productId, currentQty);
        }

        // Xử lý nút xóa
        if (e.target.matches('.remove-btn') || e.target.closest('.remove-btn')) {
            const cartItem = e.target.closest('.cart-item');
            if (cartItem) {
                Swal.fire({
                    title: 'Xác nhận',
                    text: 'Bạn có chắc muốn xóa sản phẩm này?',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Xóa',
                    cancelButtonText: 'Hủy'
                }).then((result) => {
                    if (result.isConfirmed) {
                        const productId = cartItem.dataset.id;
                        removeItem(productId);
                    }
                });
            }
        }
    });

    // Xử lý khi người dùng nhập số lượng trực tiếp
    document.body.addEventListener('change', function(e) {
        if (e.target.matches('.quantity-input')) {
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let value = parseInt(e.target.value);

            if (isNaN(value) || value < 1) {
                if (confirm('Bạn có muốn xóa sản phẩm này?')) {
                    removeItem(productId);
                } else {
                    e.target.value = '1';
                    value = 1;
                }
            } else if (value > maxStock) {
                showNotification('Vượt quá số lượng trong kho', 'error');
                e.target.value = maxStock;
                value = maxStock;
            }

            // Gửi request cập nhật
            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    id: productId,
                    quantity: value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartDropdown(data.cart_items);
                    updateCartCount(data.total_items);
                } else {
                    showNotification(data.error || 'Có lỗi xảy ra', 'error');
                    loadCartItems();
                }
            })
            .catch(error => {
                console.error('Update error:', error);
                loadCartItems();
            });
        }
    });
});

// Thêm các hàm hỗ trợ
function updateTotalAmount() {
    const allCartItems = document.querySelectorAll('.cart-item');
    const totalAmount = document.querySelector('.total-amount');
    
    if (totalAmount) {
        let total = 0;
        allCartItems.forEach(item => {
            const price = parseFloat(item.dataset.price);
            const quantity = parseInt(item.querySelector('.quantity-input').value);
            if (!isNaN(price) && !isNaN(quantity)) {
                total += price * quantity;
            }
        });
        console.log('Calculated total:', total);
        totalAmount.textContent = formatPrice(total);
    }
}

function updateCartItem(productId, quantity) {
    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Update response:', data);
        if (data.success) {
            updateCartCount(data.total_items);
        } else {
            Swal.fire({
                title: 'Lỗi',
                text: data.error || 'Có lỗi xảy ra',
                icon: 'error'
            });
            loadCartItems();
        }
    })
    .catch(error => {
        console.error('Update error:', error);
        loadCartItems();
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

