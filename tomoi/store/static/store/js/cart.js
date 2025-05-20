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
function updateCartDropdown(cartItems) {
    const cartDropdown = document.querySelector('.cart-dropdown .cart-items');
    const emptyState = document.querySelector('.cart-dropdown .empty-state');
    const totalAmount = document.querySelector('.cart-dropdown .total-amount');
    const cartCountBadge = document.querySelector('.cart-count-badge');
    
    if (!cartDropdown) return;
    
    // Xóa các mục hiện tại
    while (cartDropdown.firstChild) {
        cartDropdown.removeChild(cartDropdown.firstChild);
    }
    
    // Nếu không có sản phẩm nào, hiển thị trạng thái trống
    if (!cartItems || cartItems.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        if (totalAmount) totalAmount.textContent = '0đ';
        if (cartCountBadge) {
            cartCountBadge.textContent = '0';
            cartCountBadge.style.display = 'none';
        }
        return;
    }
    
    // Ẩn trạng thái trống
    if (emptyState) emptyState.style.display = 'none';
    
    // Cập nhật số lượng sản phẩm trong giỏ hàng
    if (cartCountBadge) {
        cartCountBadge.textContent = cartItems.length;
        cartCountBadge.style.display = 'flex';
    }
    
    // Tính tổng tiền
    let total = 0;
    
    // Thêm các sản phẩm vào dropdown
    cartItems.forEach(item => {
        total += item.price * item.quantity;
        
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.style.display = 'flex';
        cartItem.style.padding = '10px 15px';
        cartItem.style.borderBottom = '1px solid #eee';
        
        cartItem.innerHTML = `
            <div class="item-image" style="width: 50px; height: 50px; margin-right: 10px; border-radius: 4px; overflow: hidden;">
                <img src="${item.image}" alt="${item.name}" style="width: 100%; height: 100%; object-fit: cover;">
            </div>
            <div class="item-details" style="flex: 1;">
                <div class="item-name" style="font-size: 13px; font-weight: 500; margin-bottom: 3px; color: #333;">${item.name}</div>
                <div class="item-price" style="font-size: 12px; color: #e50914;">${formatPrice(item.price)} x ${item.quantity}</div>
            </div>
            <button class="remove-btn" data-id="${item.id}" style="background: none; border: none; color: #999; cursor: pointer; font-size: 14px;">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        cartDropdown.appendChild(cartItem);
        
        // Thêm event listener cho nút xóa
        const removeBtn = cartItem.querySelector('.remove-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                const itemId = this.dataset.id;
                removeFromCart(itemId);
            });
        }
    });
    
    // Cập nhật tổng tiền
    if (totalAmount) {
        totalAmount.textContent = formatPrice(total);
    }
}

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

// Khởi tạo các event listeners khi DOM đã sẵn sàng
document.addEventListener('DOMContentLoaded', function() {
  try {
        // Xử lý nút tăng/giảm số lượng
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    if (quantityBtns && quantityBtns.length > 0) {
        quantityBtns.forEach(btn => {
        btn.addEventListener('click', handleQuantityButton);
            });
    }

    // Xử lý nút xóa sản phẩm
    const removeBtns = document.querySelectorAll('.remove-btn');
    if (removeBtns && removeBtns.length > 0) {
      removeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
                const itemId = this.dataset.id;
          if (itemId) {
                removeFromCart(itemId);
        }
    });
      });
    }
  } catch (error) {
    console.error('Error initializing cart event listeners:', error);
  }
});

// Xử lý cập nhật số lượng sản phẩm
function handleQuantityButton(e) {
  try {
    const button = e.currentTarget;
    if (!button) return;
    
    const action = button.dataset.action;
    const itemId = button.dataset.id;
    if (!action || !itemId) return;
    
    const quantityInput = button.parentElement.querySelector('.quantity-input');
    if (!quantityInput) return;
    
    const currentQuantity = parseInt(quantityInput.value) || 1;
    
    let newQuantity;
    
    if (action === 'increase') {
      newQuantity = currentQuantity + 1;
    } else if (action === 'decrease') {
      newQuantity = Math.max(1, currentQuantity - 1);
    } else {
      return;
    }
    
    // Nếu số lượng không thay đổi, không làm gì cả
    if (newQuantity === currentQuantity) return;
    
    // Cập nhật hiển thị tạm thời
    quantityInput.value = newQuantity;
    
    // Hiển thị loading
    button.disabled = true;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Gửi yêu cầu cập nhật
    const csrfToken = getCookie('csrftoken');

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
        },
      body: JSON.stringify({
        item_id: itemId,
        action: action
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
        if (data.success) {
        // Reload trang khi thành công
        window.location.reload();
        } else {
        // Khôi phục trạng thái
        quantityInput.value = currentQuantity;
        button.disabled = false;
        button.innerHTML = originalText;
        
        // Hiển thị thông báo
        showToast(data.message || 'Có lỗi xảy ra', 'error');
        }
    })
    .catch(error => {
      console.error('Error updating cart item:', error);
      
      // Khôi phục trạng thái
      quantityInput.value = currentQuantity;
      button.disabled = false;
      button.innerHTML = originalText;
      
      // Hiển thị thông báo
      showToast('Có lỗi xảy ra khi kết nối đến server', 'error');
    });
  } catch (error) {
    console.error('Error handling quantity button:', error);
    showToast('Có lỗi xảy ra khi xử lý yêu cầu', 'error');
  }
}

// Xử lý xóa sản phẩm khỏi giỏ hàng
function removeFromCart(itemId) {
  if (!itemId) return;
  
    Swal.fire({
        title: 'Xác nhận xóa',
    text: 'Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Xóa',
    cancelButtonText: 'Hủy',
    confirmButtonColor: '#e50914'
    }).then((result) => {
        if (result.isConfirmed) {
      try {
        // Hiển thị loading
        Swal.fire({
          title: 'Đang xử lý',
          text: 'Vui lòng đợi trong giây lát...',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });
        
        const csrfToken = getCookie('csrftoken');
        
            fetch('/cart/remove/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
            item_id: itemId
                })
            })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
            .then(data => {
          Swal.close();
          
                if (data.success) {
            // Reload trang khi thành công
            window.location.reload();
          } else {
            // Hiển thị thông báo lỗi
            Swal.fire({
              icon: 'error',
              title: 'Lỗi',
              text: data.message || 'Có lỗi xảy ra khi xóa sản phẩm'
            });
          }
        })
        .catch(error => {
          Swal.close();
          console.error('Error removing cart item:', error);
          
          // Hiển thị thông báo lỗi
          Swal.fire({
            icon: 'error',
            title: 'Lỗi',
            text: 'Có lỗi xảy ra khi kết nối đến server'
          });
        });
      } catch (error) {
        Swal.close();
        console.error('Error in removeFromCart:', error);
        
        // Hiển thị thông báo lỗi
        Swal.fire({
          icon: 'error',
          title: 'Lỗi',
          text: 'Có lỗi xảy ra khi xử lý yêu cầu'
        });
      }
    }
  });
}

// Helper function để lấy CSRF token
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

// Helper function để hiển thị toast thông báo
function showToast(message, type = 'info') {
  if (typeof Swal !== 'undefined') {
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: type,
      title: message,
      showConfirmButton: false,
      timer: 3000
    });
  } else {
    alert(message);
  }
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
            
            fetch('/cart/apply-tcoin/', {
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
            
            fetch('/cart/apply-referral/', {
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
            
            fetch('/cart/apply-voucher/', {
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
            
            fetch('/cart/set-gift-recipient/', {
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

