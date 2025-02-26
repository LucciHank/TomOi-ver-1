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
            document.dispatchEvent(new Event('cartUpdated'));
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

// Xử lý cập nhật số lượng sản phẩm
function updateCartItem(itemId, action, value = null) {
    let data = {
        'item_id': itemId,
        'action': action
    };

    if (value !== null) {
        data.quantity = parseInt(value);
    }

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
            document.dispatchEvent(new Event('cartUpdated'));
        } else {
            Swal.fire({
                title: 'Lỗi',
                text: data.message || 'Có lỗi xảy ra',
                icon: 'error'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Xử lý xóa sản phẩm
function removeCartItem(itemId) {
    Swal.fire({
        title: 'Xác nhận xóa',
        text: 'Bạn có chắc muốn xóa sản phẩm này?',
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
                body: JSON.stringify({
                    'item_id': itemId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                    document.dispatchEvent(new Event('cartUpdated'));
                }
            });
        }
    });
}

// Xử lý toggle và submit các form promo
document.addEventListener('DOMContentLoaded', function() {
    // Toggle promo sections
    const promoHeaders = document.querySelectorAll('.promo-header');
    promoHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const targetInput = document.getElementById(targetId);
            
            // Đóng tất cả các section khác
            document.querySelectorAll('.promo-input').forEach(input => {
                if (input.id !== targetId) {
                    input.style.display = 'none';
                }
            });
            
            // Toggle section hiện tại
            if (targetInput) {
                targetInput.style.display = 
                    targetInput.style.display === 'none' ? 'block' : 'none';
            }
        });
    });

    // Xử lý TCoin
    const tcoinForm = document.getElementById('tcoinForm');
    if (tcoinForm) {
        tcoinForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const amount = document.getElementById('tcoinAmount').value;
            
            fetch('/accounts/apply-tcoin/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    amount: parseInt(amount)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                    document.dispatchEvent(new Event('cartUpdated'));
                } else {
                    Swal.fire('Lỗi', data.message, 'error');
                }
            });
        });
    }

    // Xử lý mã giới thiệu
    const referralForm = document.getElementById('referralForm');
    if (referralForm) {
        referralForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('referralCode').value;
            
            fetch('/accounts/apply-referral/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    code: code
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                    document.dispatchEvent(new Event('cartUpdated'));
                } else {
                    Swal.fire('Lỗi', data.message, 'error');
                }
            });
        });
    }

    // Xử lý mã giảm giá
    const voucherForm = document.getElementById('voucherForm');
    if (voucherForm) {
        voucherForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('voucherCode').value;
            
            fetch('/accounts/apply-voucher/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    code: code
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                    document.dispatchEvent(new Event('cartUpdated'));
                } else {
                    Swal.fire('Lỗi', data.message, 'error');
                }
            });
        });
    }

    // Xử lý tặng quà
    const giftForm = document.getElementById('giftForm');
    if (giftForm) {
        giftForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('giftEmail').value;
            
            fetch('/accounts/apply-gift/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    email: email
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                    document.dispatchEvent(new Event('cartUpdated'));
                } else {
                    Swal.fire('Lỗi', data.message, 'error');
                }
            });
        });
    }
});

// Helper function to get CSRF token
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
function addToCart(productId) {
    // ... code thêm vào giỏ hàng ...
    
    // Emit sự kiện cập nhật giỏ hàng
    document.dispatchEvent(new Event('cartUpdated'));
}

// Sau khi cập nhật số lượng
function updateQuantity(productId, quantity) {
    // ... code cập nhật số lượng ...
    
    // Emit sự kiện cập nhật giỏ hàng
    document.dispatchEvent(new Event('cartUpdated'));
}

// Sau khi xóa sản phẩm
function removeFromCart(productId) {
    // ... code xóa sản phẩm ...
    
    // Emit sự kiện cập nhật giỏ hàng
    document.dispatchEvent(new Event('cartUpdated'));
}

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
