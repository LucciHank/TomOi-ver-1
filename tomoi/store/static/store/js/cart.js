document.addEventListener('DOMContentLoaded', function () {
  const addToCartButtons = document.querySelectorAll('.add-to-cart');

  addToCartButtons.forEach(button => {
    button.addEventListener('click', function () {
      const productId = this.getAttribute('data-product-id');
      if (!productId) {
        console.error('Thiếu product ID!');
        return;
      }

      const stock = this.getAttribute('data-product-stock');
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch(`/store/add-to-cart/${productId}/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ product_id: productId, stock: stock }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert('Sản phẩm đã được thêm vào giỏ hàng!');
            updateCartDropdown(data.cart);
          } else {
            alert('Có lỗi xảy ra.');
          }
        })
        .catch(error => {
          console.error('Lỗi khi thêm vào giỏ hàng:', error);
          alert('Có lỗi xảy ra, vui lòng thử lại.');
        });
    });
  });
});

// Hàm cập nhật giỏ hàng trong giao diện người dùng
// function updateCartDropdown(cartItems) { ... }

function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price).replace('₫', 'đ');
}

function loadCartItems() {
    fetch('/cart/api/')
        .then(response => response.json())
        .then(data => {
            if (data.cart_items && data.cart_items.length > 0) {
                updateCartDropdown(data.cart_items);
                updateCartCount(data.total_items);
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateCartCount(count) {
    const badge = document.querySelector('.cart-count-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// Khởi tạo các event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Sử dụng lại các hàm từ base.js
    const cartItems = document.querySelectorAll('.cart-item');
    
    cartItems.forEach(item => {
        // Xử lý nút tăng/giảm số lượng
        const quantityBtns = item.querySelectorAll('.quantity-btn');
        quantityBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Gọi hàm handleQuantityButton từ base.js
                handleQuantityButton(e);
            });
        });

        // Xử lý nút xóa
        const removeBtn = item.querySelector('.remove-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const itemId = this.dataset.id;
                // Gọi hàm removeFromCart từ base.js
                removeFromCart(itemId);
            });
        }
    });
});

function updateQuantity(itemId, quantity) {
    const csrfToken = getCookie('csrftoken');
    
    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            itemId: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cập nhật UI
            updateCartUI(data);
        } else {
            throw new Error(data.error || 'Có lỗi xảy ra');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            title: 'Lỗi',
            text: error.message,
            icon: 'error'
        });
    });
}

function updateCartUI(data) {
    // Cập nhật số lượng
    updateCartCount(data.total_items);
    
    // Cập nhật tổng tiền
    const totalAmount = document.querySelector('.total-amount');
    if (totalAmount) {
        totalAmount.textContent = formatPrice(data.total_amount);
    }
    
    // Cập nhật tạm tính
    const subtotal = document.querySelector('.summary-details .summary-row:first-child span:last-child');
    if (subtotal) {
        subtotal.textContent = formatPrice(data.total_amount);
    }
    
    // Cập nhật tổng thanh toán
    const finalAmount = document.querySelector('.summary-details .total-row span:last-child');
    if (finalAmount) {
        finalAmount.textContent = formatPrice(data.total_amount);
    }
}

function removeCartItem(itemId) {
    Swal.fire({
        title: 'Xác nhận xóa?',
        text: "Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?",
        icon: 'warning',
        showCancelButton: true,
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
                    
                    // Cập nhật UI
                    updateCartCount(data.total_items);
                    
                    // Cập nhật tổng tiền
                    const totalAmount = document.querySelector('.total-amount');
                    if (totalAmount) {
                        totalAmount.textContent = formatPrice(data.total_amount);
                    }

                    // Nếu giỏ hàng trống
                    if (data.total_items === 0) {
                        const cartDropdown = document.querySelector('.cart-dropdown-content');
                        if (cartDropdown) {
                            cartDropdown.innerHTML = '<div class="empty-cart">Giỏ hàng trống</div>';
                        }
                    }
                }
            });
        }
    });
}

// Helper functions
function updateCartCount(count) {
    const badge = document.querySelector('.cart-count-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

function updateTotalAmount(amount) {
    const totalAmount = document.querySelector('.total-amount');
    if (totalAmount) {
        totalAmount.textContent = formatPrice(amount);
    }
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

// Thêm hàm updateCartTotal
// function updateCartTotal() { ... }

// Thêm hàm addToCart
// function addToCart(productId) { ... }

// Sửa lại event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Xử lý nút thêm vào giỏ hàng
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });

    // Xử lý nút tăng/giảm số lượng
    document.addEventListener('click', function(e) {
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
                    // Xử lý xóa sản phẩm
                    removeCartItem(itemId);
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

            updateQuantity(itemId, newQty);
        }
    });

    // Xử lý nút xóa
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.dataset.id;
            removeCartItem(itemId);
        });
    });
});

// Thêm hàm togglePromoInput
function togglePromoInput(type) {
    const input = document.getElementById(`${type}-input`);
    if (input) {
        input.style.display = input.style.display === 'none' ? 'flex' : 'none';
    }
}

// Thêm xử lý giỏ hàng trống
function showEmptyCart() {
    const cartContainer = document.querySelector('.cart-items-container');
    if (cartContainer) {
        cartContainer.innerHTML = `
            <div class="empty-cart-message">
                <i class="fas fa-shopping-cart"></i>
                <p>Giỏ hàng của bạn đang trống</p>
                <a href="/" class="btn btn-primary">Tiếp tục mua sắm</a>
            </div>
        `;
    }
}

// Thêm vào cuối file
document.addEventListener('DOMContentLoaded', function() {
    // Xử lý toggle promo inputs
    document.querySelectorAll('.promo-header').forEach(header => {
        header.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            
            // Toggle input hiện tại mà không ảnh hưởng đến các input khác
            if (input) {
                input.classList.toggle('active');
            }
        });
    });
});
