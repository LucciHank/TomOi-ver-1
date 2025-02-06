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
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation(); // Ngăn event bubble
            
            const productId = this.dataset.productId;
            const stock = parseInt(this.dataset.stock);
            
            if (stock <= 0) {
                Swal.fire({
                    title: 'Hết hàng!',
                    text: 'Sản phẩm này hiện đã hết hàng',
                    icon: 'warning'
                });
                return;
            }

            fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    id: productId,
                    quantity: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cập nhật dropdown giỏ hàng
                    updateCartDropdown(data.cart_items);
                    
                    // Cập nhật số lượng badge
                    updateCartCount(data.total_items);

                    // Hiển thị thông báo thành công
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
            if (data.cart_items) {
                updateCartDropdown(data.cart_items);
                updateCartCount(data.total_items);
            }
        })
        .catch(error => console.error('Error:', error));
}

// Thêm hàm xử lý sự kiện cho cart controls
function initCartControls() {
    // Xử lý nút tăng/giảm số lượng
    document.addEventListener('click', function(e) {
        if (e.target.matches('.quantity-btn.minus') || e.target.matches('.quantity-btn.plus')) {
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const input = cartItem.querySelector('.quantity-input');
            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let currentQty = parseInt(input.value);

            if (e.target.matches('.minus')) {
                if (currentQty <= 1) {
                    confirmRemoveItem(productId);
                    return;
                }
                currentQty--;
            } else {
                if (currentQty >= maxStock) {
                    showNotification('Vượt quá số lượng trong kho', 'error');
                    return;
                }
                currentQty++;
            }

            updateQuantity(productId, currentQty);
        }

        // Xử lý nút xóa
        if (e.target.matches('.remove-btn') || e.target.matches('.remove-btn i')) {
            const cartItem = e.target.closest('.cart-item');
            if (cartItem) {
                const productId = cartItem.dataset.id;
                confirmRemoveItem(productId);
            }
        }
    });

    // Xử lý input số lượng
    document.addEventListener('change', function(e) {
        if (e.target.matches('.quantity-input')) {
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const productId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let value = parseInt(e.target.value);

            if (isNaN(value) || value < 1) {
                confirmRemoveItem(productId);
                return;
            }
            if (value > maxStock) {
                value = maxStock;
                showNotification('Đã điều chỉnh về số lượng tối đa có sẵn', 'warning');
            }

            updateQuantity(productId, value);
        }
    });
}

// Khởi tạo các controls khi trang được load
document.addEventListener('DOMContentLoaded', function() {
    initCartControls();
    loadCartItems();
    updateCartCount();
});

// Thêm CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Xóa tất cả các hàm liên quan đến xóa sản phẩm
document.addEventListener('DOMContentLoaded', function() {
    // Chỉ giữ lại các chức năng khác của trang home
    // Ví dụ: slider, thêm vào giỏ hàng, v.v.
    
    // Xóa các event listener liên quan đến xóa sản phẩm
    const removeButtons = document.querySelectorAll('.remove-btn');
    removeButtons.forEach(btn => {
        btn.replaceWith(btn.cloneNode(true)); // Xóa tất cả event listeners
    });

    // Xóa các hàm không cần thiết
    // if (typeof showConfirmation !== 'undefined') delete showConfirmation;
    // if (typeof confirmRemoveItem !== 'undefined') delete confirmRemoveItem;
    // if (typeof removeItem !== 'undefined') delete removeItem;
});

// Chỉ giữ lại các hàm cần thiết cho trang home
function updateCartDropdown(cartItems) {
    // ... code cập nhật dropdown ...
}

function showNotification(message, type = 'success') {
    // ... code hiển thị thông báo ...
}

// Các hàm khác không liên quan đến xóa sản phẩm