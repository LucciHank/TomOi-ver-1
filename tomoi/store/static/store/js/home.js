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

    // Xóa tất cả các event listener cũ
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.replaceWith(btn.cloneNode(true));
    });

    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.replaceWith(btn.cloneNode(true));
    });

    // Load cart count khi trang web được tải
    loadCartItems();
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
    document.addEventListener('click', function (e) {
        if (e.target.matches('.quantity-btn')) {
            e.preventDefault();
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
                } else {
                    // Nếu số lượng là 1 và bấm minus, hỏi xóa sản phẩm
                    Swal.fire({
                        title: 'Xác nhận xóa?',
                        text: "Bạn có muốn xóa sản phẩm này khỏi giỏ hàng?",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#d33',
                        cancelButtonColor: '#3085d6',
                        confirmButtonText: 'Xóa',
                        cancelButtonText: 'Hủy'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            removeFromCart(itemId);
                        }
                    });
                    return;
                }
            } else if (e.target.classList.contains('plus')) {
                if (currentQty < maxStock) {
                    newQty = currentQty + 1;
                } else {
                    showNotification('Đã đạt số lượng tối đa', 'warning');
                    return;
                }
            }

            // Cập nhật số lượng
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
                        input.value = newQty;
                        updateCartCount(data.total_items);

                        // Cập nhật tổng tiền
                        const totalAmount = document.querySelector('.total-amount');
                        if (totalAmount) {
                            totalAmount.textContent = formatPrice(data.total_amount);
                        }
                    } else {
                        input.value = currentQty;
                        Swal.fire({
                            title: 'Lỗi',
                            text: data.error || 'Có lỗi xảy ra khi cập nhật giỏ hàng',
                            icon: 'error'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    input.value = currentQty;
                    Swal.fire({
                        title: 'Lỗi',
                        text: 'Không thể kết nối đến server',
                        icon: 'error'
                    });
                });
        }
    });
}

// Khởi tạo các controls khi trang được load
document.addEventListener('DOMContentLoaded', function () {
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
document.addEventListener('DOMContentLoaded', function () {
    // Chỉ giữ lại các chức năng khác của trang home
    // Ví dụ: slider, thêm vào giỏ hàng, v.v.
});

// Chỉ giữ lại các hàm cần thiết cho trang home
function updateCartDropdown(cartItems) {
    // ... code cập nhật dropdown ...
}

function showNotification(message, type = 'success') {
    // ... code hiển thị thông báo ...
}

// Các hàm khác không liên quan đến xóa sản phẩm

function toggleWishlist(button, event) {
    event.preventDefault();
    event.stopPropagation();

    if (!document.body.dataset.userAuthenticated) {
        Swal.fire({
            title: 'Yêu cầu đăng nhập',
            text: 'Vui lòng đăng nhập để sử dụng tính năng này',
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: 'Đăng nhập',
            cancelButtonText: 'Hủy'
        }).then((result) => {
            if (result.isConfirmed) {
                // Mở modal đăng nhập
                $('#loginModal').modal('show');
            }
        });
        return;
    }

    const productId = button.dataset.productId;
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/store/toggle-wishlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            button.classList.add('active');
            button.querySelector('i').classList.remove('far');
            button.querySelector('i').classList.add('fas');
        } else if (data.status === 'removed') {
            button.classList.remove('active');
            button.querySelector('i').classList.remove('fas');
            button.querySelector('i').classList.add('far');
        }
        
        Swal.fire({
            text: data.message,
            icon: data.status === 'error' ? 'error' : 'success',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            text: 'Có lỗi xảy ra',
            icon: 'error',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    });
}