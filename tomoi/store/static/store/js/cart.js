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
    // Xử lý nút xóa (thùng rác)
    document.querySelectorAll('.remove-btn, .btn-remove').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const itemId = this.dataset.id;
            removeCartItem(itemId);
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
                }
            } else if (e.target.classList.contains('plus')) {
                if (currentQty < maxStock) {
                    newQty = currentQty + 1;
                }
            }

            if (newQty !== currentQty) {
                // Cập nhật UI trước
                input.value = newQty;
                
                // Gọi API để cập nhật server
                fetch('/cart/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({
                        product_id: itemId,
                        quantity: newQty
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Cập nhật tổng giá
                        const totalAmount = document.querySelector('.total-amount');
                        if (totalAmount) {
                            totalAmount.textContent = formatPrice(data.total_amount);
                        }
                        
                        // Cập nhật giá của item
                        const priceElement = cartItem.querySelector('.current-price');
                        if (priceElement) {
                            priceElement.textContent = formatPrice(data.item_price);
                        }
                        
                        // Cập nhật số lượng trong badge
                        updateCartCount(data.total_items);
                    } else {
                        // Nếu có lỗi, khôi phục lại số lượng cũ
                        input.value = currentQty;
                        Swal.fire({
                            title: 'Lỗi',
                            text: data.error || 'Có lỗi xảy ra khi cập nhật giỏ hàng',
                            icon: 'error'
                        });
                    }
                })
                .catch(error => {
                    // Nếu có lỗi kết nối, khôi phục lại số lượng cũ
                    input.value = currentQty;
                    console.error('Error:', error);
                    Swal.fire({
                        title: 'Lỗi',
                        text: 'Không thể kết nối đến server',
                        icon: 'error'
                    });
                });
            }
        }
    });

    // Xử lý nút xóa sản phẩm
    document.addEventListener('click', function(e) {
        if (e.target.matches('.remove-btn') || e.target.closest('.remove-btn')) {
            e.preventDefault();
            const cartItem = e.target.closest('.cart-item');
            if (!cartItem) return;

            const itemId = cartItem.dataset.id;
            removeCartItem(itemId);
        }
    });

    // Xử lý nhập số lượng trực tiếp
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const cartItem = this.closest('.cart-item');
            const itemId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            let value = parseInt(this.value);

            if (isNaN(value) || value < 1) {
                removeCartItem(itemId);
                return;
            }

            if (value > maxStock) {
                value = maxStock;
                this.value = maxStock;
                Swal.fire({
                    title: 'Thông báo',
                    text: 'Vượt quá số lượng trong kho',
                    icon: 'warning'
                });
            }

            updateQuantity(itemId, value);
        });
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
            product_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cập nhật tổng giá
            const totalAmount = document.querySelector('.total-amount');
            if (totalAmount) {
                totalAmount.textContent = formatPrice(data.total_amount);
            }
            
            // Cập nhật giá của item
            const cartItem = document.querySelector(`.cart-item[data-id="${itemId}"]`);
            if (cartItem) {
                const priceElement = cartItem.querySelector('.current-price');
                if (priceElement) {
                    priceElement.textContent = formatPrice(data.item_price);
                }
            }
            
            // Cập nhật số lượng trong badge
            updateCartCount(data.total_items);
        } else {
            // Nếu có lỗi, khôi phục lại số lượng cũ
            const input = document.querySelector(`.cart-item[data-id="${itemId}"] .quantity-input`);
            if (input) {
                input.value = data.old_quantity || 1;
            }
            
            Swal.fire({
                title: 'Lỗi',
                text: data.error || 'Có lỗi xảy ra khi cập nhật giỏ hàng',
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

    // Các event listeners khác giữ nguyên...
  });
