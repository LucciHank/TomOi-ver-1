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
    document.querySelectorAll('.btn-quantity').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const cartItem = this.closest('.cart-item');
            const itemId = cartItem.dataset.id;
            const maxStock = parseInt(cartItem.dataset.stock);
            const input = cartItem.querySelector('.quantity-input');
            let currentQty = parseInt(input.value);

            if (this.classList.contains('minus')) {
                if (currentQty <= 1) {
                    // Nếu số lượng giảm xuống 0, hỏi xóa sản phẩm
                    removeCartItem(itemId);
                    return;
                }
                currentQty--;
            } else if (this.classList.contains('plus')) {
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

            updateQuantity(itemId, currentQty);
        });
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
    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cập nhật UI
            document.querySelectorAll(`.cart-item[data-id="${itemId}"] .quantity-input`)
                .forEach(input => input.value = quantity);

            // Cập nhật tổng tiền
            updateTotalAmount(data.total_amount);
            
            // Cập nhật số lượng badge
            updateCartCount(data.total_items);
        } else {
            Swal.fire({
                title: 'Lỗi!',
                text: data.error || 'Có lỗi xảy ra',
                icon: 'error'
            });
        }
    })
    .catch(error => {
        console.error('Update error:', error);
        Swal.fire({
            title: 'Lỗi!',
            text: 'Không thể kết nối đến server',
            icon: 'error'
        });
    });
}

function removeCartItem(itemId) {
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
                body: JSON.stringify({ id: itemId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Tải lại toàn bộ giỏ hàng thay vì chỉ xóa phần tử
                    loadCartItems();
                    
                    // Cập nhật UI
                    updateCartCount(data.total_items);
                    updateTotalAmount(data.total_amount);

                    Swal.fire({
                        title: 'Đã xóa!',
                        text: 'Sản phẩm đã được xóa khỏi giỏ hàng',
                        icon: 'success',
                        timer: 1500,
                        showConfirmButton: false
                    });

                    // Nếu giỏ hàng trống, reload trang
                    if (data.total_items === 0) {
                        location.reload();
                    }
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
