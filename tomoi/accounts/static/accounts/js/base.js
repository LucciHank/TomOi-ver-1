// Biến để kiểm tra xem script đã được load chưa
if (typeof baseJsLoaded === 'undefined') {
    const baseJsLoaded = true;
    console.log('Base.js loading...');

    // Hàm xử lý chính
    function initBaseJS() {
        console.log('Initializing base.js');
        loadCartItems();

        // Chỉ thêm event listener một lần
        document.removeEventListener('click', handleGlobalClick);
        document.addEventListener('click', handleGlobalClick);
    }

    // Tách riêng hàm xử lý click để dễ quản lý
    function handleGlobalClick(e) {
        // Xử lý nút xóa
        const removeBtn = e.target.closest('.remove-btn');
        if (removeBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            const itemId = removeBtn.dataset.id;
            if (itemId) {
                removeFromCart(itemId, false); // Luôn hiện dialog xác nhận khi bấm nút xóa
            }
            return; // Thêm return để tránh xử lý các event khác
        }

        // Xử lý nút tăng/giảm số lượng
        if (e.target.matches('.quantity-btn')) {
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const input = cartItem.querySelector('.quantity-input');
            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let currentQty = parseInt(input.value);

            if (e.target.classList.contains('minus')) {
                currentQty--;
                if (currentQty <= 0) {
                    removeFromCart(productId, false); // Hiện dialog xác nhận khi giảm về 0
                    return;
                }
                updateCartItem(productId, currentQty);
            } else if (e.target.classList.contains('plus')) {
                if (currentQty < maxStock) {
                    currentQty++;
                    updateCartItem(productId, currentQty);
                }
            }
            return; // Thêm return để tránh xử lý các event khác
        }

        // Xử lý input số lượng
        if (e.target.matches('.quantity-input')) {
            const input = e.target;
            const cartItem = input.closest('.cart-item');
            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);

            // Xóa event listener cũ nếu có
            input.removeEventListener('change', handleQuantityChange);
            
            // Thêm event listener mới
            input.addEventListener('change', handleQuantityChange);
        }
    }

    // Tách riêng hàm xử lý thay đổi số lượng
    function handleQuantityChange() {
        const cartItem = this.closest('.cart-item');
        const productId = cartItem.dataset.id;
        const maxStock = parseInt(cartItem.dataset.stock);
        let value = parseInt(this.value);

        if (isNaN(value) || value <= 0) {
            removeFromCart(productId, false); // Hiện dialog xác nhận khi nhập số <= 0
            return;
        }
        if (value > maxStock) {
            value = maxStock;
        }

        this.value = value;
        updateCartItem(productId, value);
    }

    function removeFromCart(itemId, skipConfirmation = false) {
        // Nếu không skip confirmation thì hiện dialog xác nhận
        if (!skipConfirmation) {
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
                    // Nếu xác nhận xóa thì gọi lại hàm với skipConfirmation = true
                    removeFromCart(itemId, true);
                } else {
                    // Nếu hủy xóa, reset lại số lượng về 1
                    const input = document.querySelector(`.cart-item[data-id="${itemId}"] .quantity-input`);
                    if (input) {
                        input.value = 1;
                        updateCartItem(itemId, 1);
                    }
                }
            });
            return;
        }

        // Phần xử lý xóa thực tế
        fetch('/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ id: itemId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                loadCartItems();
                updateCartCount(data.total_items);

                // Chỉ hiện thông báo thành công khi đã xác nhận xóa
                Swal.fire({
                    title: 'Đã xóa!',
                    text: 'Sản phẩm đã được xóa khỏi giỏ hàng',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                throw new Error(data.error || 'Có lỗi xảy ra');
            }
        })
        .catch(error => {
            console.error('Remove error:', error);
            Swal.fire({
                title: 'Lỗi!',
                text: error.message || 'Không thể kết nối đến server',
                icon: 'error'
            });
        });
    }

    // Khởi tạo khi DOM đã sẵn sàng
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBaseJS);
    } else {
        initBaseJS();
    }
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
    // Cập nhật tất cả các container giỏ hàng trên trang
    const cartContainers = document.querySelectorAll('.cart-items');
    const emptyCartMessages = document.querySelectorAll('.empty-cart');
    const totalAmounts = document.querySelectorAll('.total-amount');

    if (!cartItems || cartItems.length === 0) {
        emptyCartMessages.forEach(msg => msg.style.display = 'block');
        cartContainers.forEach(container => container.innerHTML = '');
        totalAmounts.forEach(total => total.textContent = '0đ');
        return;
    }

    emptyCartMessages.forEach(msg => msg.style.display = 'none');
    
    const cartItemHTML = cartItems.map(item => `
        <div class="cart-item" data-id="${item.id}" data-stock="${item.stock}" data-price="${item.price}">
            <div class="item-image">
                <img src="${item.image || '/static/images/placeholder.png'}" alt="${item.name}">
            </div>
            <div class="item-content">
                <div class="item-info">
                    <h6 class="item-name">${item.name}</h6>
                    <div class="item-price">
                        <span class="current-price">${formatPrice(item.price)}</span>
                        <div class="price-secondary">
                            ${item.old_price ? `
                                <span class="old-price">${formatPrice(item.old_price)}</span>
                                <span class="discount-badge">-${Math.round(((item.old_price - item.price) / item.old_price) * 100)}%</span>
                            ` : ''}
                        </div>
                    </div>
                </div>
                <div class="item-controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn minus" ${item.quantity <= 1 ? 'disabled' : ''}>-</button>
                        <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="${item.stock}">
                        <button class="quantity-btn plus" ${item.quantity >= item.stock ? 'disabled' : ''}>+</button>
                    </div>
                    <button class="remove-btn" data-id="${item.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Cập nhật nội dung cho tất cả các container
    cartContainers.forEach(container => {
        container.innerHTML = cartItemHTML;
    });

    // Cập nhật tổng tiền cho tất cả các phần hiển thị tổng
    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    totalAmounts.forEach(totalEl => {
        totalEl.textContent = formatPrice(total);
    });

    // Cập nhật badge số lượng
    updateCartCount(cartItems.reduce((sum, item) => sum + item.quantity, 0));
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
        
        // Cập nhật UI ngay lập tức
        totalAmount.textContent = formatPrice(total);
        
        // Lưu giá trị tạm thời
        totalAmount.dataset.currentTotal = total;
    }
}

function updateCartItem(productId, quantity) {
    // Cập nhật UI ngay lập tức để tránh nhấp nháy
    const input = document.querySelector(`.cart-item[data-id="${productId}"] .quantity-input`);
    if (input) input.value = quantity;
    
    // Tính toán và cập nhật tổng tiền tạm thời
    updateTotalAmount();

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
        if (data.success) {
            loadCartItems();
        } else {
            Swal.fire({
                title: 'Lỗi',
                text: data.error || 'Có lỗi xảy ra',
                icon: 'error'
            });
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

