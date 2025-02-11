// Biến để kiểm tra xem script đã được load chưa
if (typeof baseJsLoaded === 'undefined') {
    const baseJsLoaded = true;
    console.log('Base.js loading...');

    // Thêm biến để kiểm soát hover và update
    let isHovering = false;
    let isUpdating = false;
    let isProcessing = false;
    let debounceTimer;

    // Hàm khởi tạo
    function initBaseJS() {
        console.log('Initializing base.js');
        
        // Load giỏ hàng ngay khi trang load
        loadCartItems();
        updateCartBadge();
        
        // Xóa event listener cũ trước khi thêm mới
        document.removeEventListener('click', handleGlobalClick);
        document.addEventListener('click', handleGlobalClick);
        
        // Thêm event listener cho hover giỏ hàng
        const cartWrapper = document.querySelector('.cart-wrapper');
        if (cartWrapper) {
            cartWrapper.removeEventListener('mouseenter', handleCartHover);
            cartWrapper.addEventListener('mouseenter', handleCartHover);
            
            cartWrapper.removeEventListener('mouseleave', handleCartLeave);
            cartWrapper.addEventListener('mouseleave', handleCartLeave);
        }
    }

    // Tách riêng handler cho hover
    function handleCartHover() {
        if (!isHovering && !isUpdating) {
            isHovering = true;
            loadCartItems();
        }
    }
            
    function handleCartLeave() {
        isHovering = false;
    }

    // Xử lý click cho quantity buttons
    function handleGlobalClick(e) {
        if (e.target.matches('.quantity-btn') && !isProcessing) {
            e.preventDefault();
            e.stopPropagation();

            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const input = cartItem.querySelector('.quantity-input');
            const itemId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let currentQty = parseInt(input.value);
            let newQty = currentQty;

            if (e.target.classList.contains('minus')) {
                if (currentQty > 1) {
                    newQty = currentQty - 1;
                }
            } else if (e.target.classList.contains('plus')) {
                if (currentQty < maxStock) {
                    newQty = currentQty + 1;
                } else {
                    showNotification('Đã đạt số lượng tối đa', 'warning');
                    return;
                }
            }

            if (newQty !== currentQty) {
                updateCartQuantity(itemId, newQty, input, currentQty);
            }
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
        if (isUpdating) return; // Nếu đang cập nhật thì không load lại

        fetch('/cart/api/')
            .then(response => response.json())
            .then(data => {
                updateCartUI(data);
                updateCartCount(data.total_items);
            })
            .catch(error => {
                console.error('Error loading cart items:', error);
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

    // Thêm hàm validateProductData
    function validateProductData(productData) {
        // Kiểm tra user đã đăng nhập chưa
        const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
        if (!isAuthenticated) {
            Swal.fire({
                title: 'Yêu cầu đăng nhập',
                text: 'Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Đăng nhập',
                cancelButtonText: 'Hủy'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Hiển thị modal đăng nhập
                    const loginModal = new bootstrap.Modal(document.getElementById('authModal'));
                    loginModal.show();
                }
            });
            return false;
        }

        // Kiểm tra thông tin email nếu sản phẩm yêu cầu
        if (productData.requires_email && !productData.upgrade_email) {
            Swal.fire({
                title: 'Thiếu thông tin',
                text: 'Vui lòng nhập email cần nâng cấp',
                icon: 'warning'
            });
            return false;
        }

        // Kiểm tra thông tin tài khoản nếu sản phẩm yêu cầu
        if (productData.requires_account_password && 
            (!productData.account_username || !productData.account_password)) {
            Swal.fire({
                title: 'Thiếu thông tin',
                text: 'Vui lòng nhập đầy đủ thông tin tài khoản cần nâng cấp',
                icon: 'warning'
            });
            return false;
        }

        return true;
    }

    // Sửa lại hàm addToCart
    function addToCart(productData) {
        // Validate dữ liệu trước khi thêm vào giỏ
        if (!validateProductData(productData)) {
            return;
        }

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(productData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Cập nhật UI giỏ hàng
                updateCartDropdown(data.cart_items);
                updateCartCount(data.total_items);
                
                Swal.fire({
                    title: 'Thành công!',
                    text: 'Đã thêm sản phẩm vào giỏ hàng',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                });
            } else {
                throw new Error(data.error || 'Có lỗi xảy ra');
            }
        })
        .catch(error => {
            console.error('Add to cart error:', error);
            Swal.fire({
                title: 'Lỗi!',
                text: error.message || 'Không thể thêm sản phẩm vào giỏ hàng',
                icon: 'error'
            });
        });
    }

    // Tách riêng phần cập nhật UI
    function updateCartUI(data) {
        if (!data || !data.cart_items) return;  // Thêm kiểm tra data

        const cartContainers = document.querySelectorAll('.cart-items');
        const emptyCartMessages = document.querySelectorAll('.empty-cart');
        const totalAmounts = document.querySelectorAll('.total-amount');

        // Nếu giỏ hàng trống
        if (!data.cart_items.length) {
            emptyCartMessages.forEach(msg => msg.style.display = 'block');
            cartContainers.forEach(container => container.innerHTML = '');
            totalAmounts.forEach(total => total.textContent = '0đ');
            return;
        }

        // Nếu có sản phẩm trong giỏ hàng
        emptyCartMessages.forEach(msg => msg.style.display = 'none');

        const cartItemHTML = data.cart_items.map(item => {
            // Tính giá cho một đơn vị sản phẩm (không nhân với số lượng)
            const unitPrice = item.price;
            
            return `
                <div class="cart-item" data-id="${item.id}" data-stock="${item.stock}">
                    <div class="item-image">
                        <img src="${item.image || '/static/images/placeholder.png'}" alt="${item.name}">
                    </div>
                    <div class="item-content">
                        <div class="item-info">
                            <h6 class="item-name">${item.name}</h6>
                            <div class="item-price-wrapper">
                                <span class="current-price">${formatPrice(unitPrice)}</span>
                            </div>
                            <div class="item-details">
                                <span class="account-type">${item.variant_name || ''}</span>
                                <span class="duration">${item.duration || ''} tháng</span>
                            </div>
                        </div>
                        <div class="item-controls">
                            <div class="quantity-controls">
                                <button class="quantity-btn minus" data-id="${item.id}">-</button>
                                <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="${item.stock}" readonly>
                                <button class="quantity-btn plus" data-id="${item.id}">+</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // Cập nhật nội dung giỏ hàng
        cartContainers.forEach(container => {
            container.innerHTML = cartItemHTML;
        });

        // Cập nhật tổng tiền
        if (data.cart_items && data.cart_items.length > 0) {
            const totalAmount = data.cart_items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            totalAmounts.forEach(total => {
                total.textContent = formatPrice(totalAmount);
            });
        } else {
            totalAmounts.forEach(total => {
                total.textContent = '0đ';
            });
        }
    }

    // Thêm hàm updateCartDropdown
    function updateCartDropdown(cartItems) {
        const cartItemsContainer = document.querySelector('.cart-items');
        const emptyCartMessage = document.querySelector('.empty-cart');
        const totalAmountElement = document.querySelector('.total-amount');
        
        if (!cartItems || cartItems.length === 0) {
            if (cartItemsContainer) cartItemsContainer.innerHTML = '';
            if (emptyCartMessage) emptyCartMessage.style.display = 'block';
            if (totalAmountElement) totalAmountElement.textContent = '0đ';
            return;
        }

        if (emptyCartMessage) emptyCartMessage.style.display = 'none';

        const cartHTML = cartItems.map(item => `
            <div class="cart-item" data-id="${item.id}" data-stock="${item.stock}" data-price="${item.price}">
                <div class="item-image">
                    <img src="${item.image || '/static/images/placeholder.png'}" alt="${item.name}">
                </div>
                <div class="item-content">
                    <div class="item-info">
                        <h6 class="item-name">${item.name}</h6>
                        <div class="item-price-wrapper">
                            <span class="current-price">${formatPrice(item.price * item.quantity)}</span>
                            ${item.old_price ? `
                                <span class="old-price">${formatPrice(item.old_price * item.quantity)}</span>
                                <span class="discount-badge">-${item.discount}%</span>
                            ` : ''}
                        </div>
                        <div class="item-details">
                            <span class="account-type">${item.variant_name}</span>
                            <span class="duration">${item.duration} tháng</span>
                        </div>
                    </div>
                    <div class="item-controls-wrapper">
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

        if (cartItemsContainer) {
            cartItemsContainer.innerHTML = cartHTML;
        }

        // Tính tổng tiền
        const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        if (totalAmountElement) {
            totalAmountElement.textContent = formatPrice(total);
        }
    }

    // Thêm hàm updateCartCount
    function updateCartCount(count = 0) {
        const badge = document.querySelector('.cart-count-badge');
        if (!badge) return;

        // Kiểm tra user đã đăng nhập chưa
        const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
        
        if (!isAuthenticated) {
            // Nếu chưa đăng nhập, ẩn badge và set count = 0
            badge.style.display = 'none';
            badge.textContent = '0';
            badge.dataset.count = '0';
            return;
        }

        // Nếu đã đăng nhập
        badge.dataset.count = count;
        badge.textContent = count;
        
        // Chỉ hiển thị khi có sản phẩm
        if (count > 0) {
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }

    // Thêm hàm updateCartBadge
    function updateCartBadge() {
        fetch('/cart/api/')
            .then(response => response.json())
            .then(data => {
                const cartCountBadge = document.querySelector('.cart-count-badge');
                if (cartCountBadge) {
                    const count = data.total_items;
                    cartCountBadge.textContent = count;
                    cartCountBadge.style.display = count > 0 ? 'inline' : 'none';
                }
            })
            .catch(error => console.error('Error updating cart badge:', error));
    }

    // Thêm hàm removeCartItem
    function removeCartItem(itemId) {
        fetch('/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ id: itemId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Xóa phần tử khỏi DOM
                const cartItem = document.querySelector(`.cart-item[data-id="${itemId}"]`);
                if (cartItem) {
                    cartItem.remove();
                }
                
                // Cập nhật số lượng trong badge
                updateCartCount(data.total_items);

                // Nếu giỏ hàng trống
                if (data.total_items === 0) {
                    const cartDropdown = document.querySelector('.cart-dropdown-content');
                    if (cartDropdown) {
                        const emptyCartHTML = `
                            <div class="empty-cart">
                                <i class="fas fa-shopping-cart"></i>
                                <p>Bạn chưa có sản phẩm nào trong giỏ hàng</p>
                            </div>
                            <div class="cart-total">
                                <span>Tổng cộng:</span>
                                <span class="total-amount">0đ</span>
                            </div>
                            <div class="cart-footer">
                                <a href="/cart/" class="btn btn-primary">Xem giỏ hàng</a>
                                <a href="#" class="btn btn-checkout">Thanh toán ngay</a>
                            </div>
                        `;
                        cartDropdown.innerHTML = emptyCartHTML;
                    }
                } else {
                    // Cập nhật tổng tiền nếu còn sản phẩm
                    const totalAmount = document.querySelector('.total-amount');
                    if (totalAmount) {
                        totalAmount.textContent = formatPrice(data.total_amount);
                    }
                }
            } else {
                Swal.fire({
                    title: 'Lỗi',
                    text: data.error || 'Có lỗi xảy ra khi xóa sản phẩm',
                    icon: 'error'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Lỗi',
                text: 'Không thể kết nối đến server',
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

    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Đóng modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('authModal'));
                modal.hide();
                
                // Hiển thị thông báo thành công
                Swal.fire({
                    title: 'Thành công!',
                    text: data.message || 'Đăng nhập thành công!',
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    // Reload trang thay vì chỉ redirect
                    window.location.reload();
                });
            } else {
                Swal.fire({
                    title: 'Lỗi',
                    text: data.error || 'Có lỗi xảy ra',
                    icon: 'error'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Lỗi',
                text: 'Có lỗi xảy ra khi đăng nhập',
                icon: 'error'
            });
        });
    });

    // Thêm hàm kiểm tra trạng thái đăng nhập
    function checkLoginStatus() {
        const userAuthenticated = document.body.dataset.userAuthenticated === 'true';
        const userDropdown = document.querySelector('.dropdown-content');
        const loginButton = document.querySelector('[data-bs-target="#authModal"]');
        
        if (userAuthenticated) {
            if (loginButton) loginButton.style.display = 'none';
            if (userDropdown) userDropdown.classList.add('authenticated');
        } else {
            if (loginButton) loginButton.style.display = 'block';
            if (userDropdown) userDropdown.classList.remove('authenticated');
        }
    }

    // Chạy kiểm tra khi trang load
    document.addEventListener('DOMContentLoaded', checkLoginStatus);

    // Thêm event listener cho window load
    window.addEventListener('load', function() {
        loadCartItems();
        updateCartBadge();
    });

    // Gọi loadCartItems khi trang load và sau khi đăng xuất
    document.addEventListener('DOMContentLoaded', loadCartItems);

    // Thêm event listener cho nút đăng xuất
    document.querySelector('.logout-btn')?.addEventListener('click', function() {
        // Xóa giỏ hàng khi đăng xuất
        updateCartDropdown([]);
        updateCartCount(0);
    });

    // Sửa lại hàm updateCartQuantity
    function updateCartQuantity(itemId, newQty, input, currentQty) {
        if (isProcessing) return;
        isProcessing = true;

        fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                itemId: itemId,
                quantity: newQty
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Cập nhật số lượng trên tất cả các input có cùng itemId
                document.querySelectorAll(`.cart-item[data-id="${itemId}"] .quantity-input`).forEach(input => {
                    input.value = newQty;
                });

                // Cập nhật UI giỏ hàng
                if (data.cart_items) {
                    updateCartUI({cart_items: data.cart_items});
                    updateCartCount(data.total_items);
                }

                // Cập nhật tổng tiền nếu có
                if (data.total_amount) {
                    document.querySelectorAll('.total-amount').forEach(total => {
                        total.textContent = formatPrice(data.total_amount);
                    });
                }
            } else {
                // Khôi phục giá trị cũ nếu có lỗi
                input.value = currentQty;
                throw new Error(data.error || 'Có lỗi xảy ra khi cập nhật giỏ hàng');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                title: 'Lỗi',
                text: error.message || 'Không thể kết nối đến server',
                icon: 'error'
            });
            // Khôi phục giá trị cũ
            input.value = currentQty;
        })
        .finally(() => {
            setTimeout(() => {
                isProcessing = false;
            }, 300);
        });
    }
}

