// Biến để kiểm tra xem script đã được load chưa
if (typeof baseJsLoaded === 'undefined') {
    const baseJsLoaded = true;
    console.log('Base.js loading...');

    // Thêm biến để kiểm soát hover và update
    let isHovering = false;
    let isUpdating = false;

    // Hàm khởi tạo
    function initBaseJS() {
        console.log('Initializing base.js');
        
        // Load giỏ hàng ban đầu
        loadCartItems();
        
        // Thêm event listener cho click toàn cục
        document.removeEventListener('click', handleGlobalClick);
        document.addEventListener('click', handleGlobalClick);
        
        // Thêm event listener cho hover giỏ hàng
        const cartWrapper = document.querySelector('.cart-wrapper');
        if (cartWrapper) {
            cartWrapper.addEventListener('mouseenter', function() {
                if (!isHovering && !isUpdating) {
                    isHovering = true;
                    loadCartItems();
                }
            });
            
            cartWrapper.addEventListener('mouseleave', function() {
                isHovering = false;
            });
        }
    }

    // Tách riêng hàm xử lý click để dễ quản lý
    function handleGlobalClick(e) {
        // Xử lý nút tăng/giảm số lượng
        if (e.target.matches('.quantity-btn')) {
            e.preventDefault();
            e.stopPropagation();
            
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const input = cartItem.querySelector('.quantity-input');
            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let currentQty = parseInt(input.value);

            if (e.target.classList.contains('minus')) {
                if (currentQty > 1) {
                    currentQty--;
                    updateCartItem(productId, currentQty);
                } else {
                    removeFromCart(productId, false);
                }
            } else if (e.target.classList.contains('plus')) {
                if (currentQty < maxStock) {
                    currentQty++;
                    updateCartItem(productId, currentQty);
                }
            }
            return;
        }

        // Xử lý nút xóa
        const removeBtn = e.target.closest('.remove-btn');
        if (removeBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            const itemId = removeBtn.dataset.id;
            if (itemId) {
                removeFromCart(itemId, false);
            }
            return;
        }
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

    function loadCartItems() {
        if (isUpdating) return; // Nếu đang update thì không load

        fetch('/cart/api/')
            .then(response => response.json())
            .then(data => {
                // Cập nhật UI
                updateCartUI(data);
            })
            .catch(error => {
                console.error('Error loading cart:', error);
            });
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

    function updateQuantity(productId, quantity) {
        updateCartItem(productId, quantity);
    }

    function updateCartItem(productId, quantity) {
        if (isUpdating) return;
        isUpdating = true;

        // Cập nhật UI ngay lập tức
        const input = document.querySelector(`.cart-item[data-id="${productId}"] .quantity-input`);
        if (input) {
            input.value = quantity;
        }

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
                // Cập nhật badge số lượng
                if (data.total_items) {
                    updateCartCount(data.total_items);
                }

                // Cập nhật tổng tiền và UI
                if (data.cart_items) {
                    updateCartUI({
                        cart_items: data.cart_items,
                        total_items: data.total_items
                    });
                }
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
        })
        .finally(() => {
            setTimeout(() => {
                isUpdating = false;
            }, 300);
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

    // Thêm hàm addToCart
    function addToCart(productId) {
        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ id: productId, quantity: 1 })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadCartItems(); // Tải lại toàn bộ giỏ hàng
                Swal.fire({
                    title: 'Thành công!',
                    text: 'Đã thêm sản phẩm vào giỏ hàng',
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
            console.error('Add to cart error:', error);
            Swal.fire({
                title: 'Lỗi!',
                text: 'Không thể kết nối đến server',
                icon: 'error'
            });
        });
    }

    // Tách riêng phần cập nhật UI
    function updateCartUI(data) {
        const cartContainers = document.querySelectorAll('.cart-items');
        const emptyCartMessages = document.querySelectorAll('.empty-cart');
        const totalAmounts = document.querySelectorAll('.total-amount');

        if (!data.cart_items || data.cart_items.length === 0) {
            emptyCartMessages.forEach(msg => msg.style.display = 'block');
            cartContainers.forEach(container => container.innerHTML = '');
            totalAmounts.forEach(total => total.textContent = '0đ');
            return;
        }

        // Cập nhật UI giỏ hàng
        emptyCartMessages.forEach(msg => msg.style.display = 'none');
        
        const cartItemHTML = data.cart_items.map(item => `
            <div class="cart-item" data-id="${item.id}" data-stock="${item.stock}" data-price="${item.price}">
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

        cartContainers.forEach(container => {
            container.innerHTML = cartItemHTML;
        });

        // Tính và cập nhật tổng tiền
        const total = data.cart_items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        console.log('Updating total amount:', total); // Debug log
        totalAmounts.forEach(totalEl => {
            totalEl.textContent = formatPrice(total);
        });
    }

    // Khởi tạo khi DOM đã sẵn sàng
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBaseJS);
    } else {
        initBaseJS();
    }
}

