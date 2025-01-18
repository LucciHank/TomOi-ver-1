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
function updateCartDropdown(cart) {
  const cartItemsList = document.querySelector("#cart-items-list");
  cartItemsList.innerHTML = "";  // Xóa giỏ hàng cũ

  if (Object.keys(cart).length === 0) {
    cartItemsList.innerHTML = "<li>Giỏ hàng trống</li>";
  } else {
    // Hiển thị lại giỏ hàng với sản phẩm và số lượng mới
    for (let productId in cart) {
      const item = cart[productId];
      const li = document.createElement("li");
      li.textContent = `${item.name} x ${item.quantity} - ${item.price * item.quantity} VNĐ`;
      cartItemsList.appendChild(li);
    }
  }
}

document.getElementById('cartDropdown').addEventListener('mouseover', function () {
  fetch('/cart/api/')
    .then(response => response.json())
    .then(data => {
      const cartItemsList = document.getElementById('cart-items-list');
      cartItemsList.innerHTML = ''; // Xóa các sản phẩm cũ trong giỏ hàng khi hover

      // Hiển thị sản phẩm trong giỏ hàng
      data.cart.forEach(item => {
        const li = document.createElement('li');

        // Sử dụng Intl.NumberFormat để định dạng giá tiền với dấu phẩy
        const formattedPrice = new Intl.NumberFormat('vi-VN').format(item.total_price);
        li.textContent = `${item.name} x${item.quantity} - ${formattedPrice} VND`;

        cartItemsList.appendChild(li);
      });

      // Cập nhật tổng số lượng
      document.getElementById('cart-count').textContent = data.total_items;
    });
});


function updateCartDropdown(cart) {
  const cartItemsList = document.querySelector("#cart-items-list");
  cartItemsList.innerHTML = "";  // Xóa giỏ hàng cũ

  if (Object.keys(cart).length === 0) {
    cartItemsList.innerHTML = "<li>Giỏ hàng trống</li>";
  } else {
    // Cập nhật giỏ hàng dưới dạng card bo góc
    for (let productId in cart) {
      const item = cart[productId];
      const card = document.createElement("div");
      card.classList.add("cart-card");
      card.innerHTML = `
                <div class="card">
                    <img src="${item.image}" class="card-img-top" alt="${item.name}">
                    <div class="card-body">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text">Số lượng: ${item.quantity}</p>
                        <p class="card-text">Giá: ${item.price * item.quantity} VND</p>
                    </div>
                </div>
            `;
      cartItemsList.appendChild(card);
    }
  }
}

function formatCurrency(number) {
  return number.toLocaleString();  // Format giá thành dạng tiền tệ (sử dụng dấu phẩy)
}

// Cập nhật trong cart.js hoặc trong HTML để hiển thị giá
document.querySelectorAll('.product-price').forEach(function (element) {
  let price = parseFloat(element.textContent);
  element.textContent = formatCurrency(price) + ' VND';  // Hiển thị dưới dạng tiền tệ
});

document.querySelectorAll('.cart-price').forEach(function (element) {
  let price = parseFloat(element.textContent);
  element.textContent = formatCurrency(price) + ' VND';  // Hiển thị dưới dạng tiền tệ
});

// Trong phần cập nhật giỏ hàng (bên trong forEach):
fetch('/cart/api/')
  .then(response => response.json())
  .then(data => {
    // Cập nhật giỏ hàng
    const cartItemsList = document.getElementById('cart-items-list');
    cartItemsList.innerHTML = '';  // Xóa nội dung cũ
    data.cart.forEach(item => {
      const li = document.createElement('li');
      // Sử dụng formatCurrency để hiển thị giá
      const formattedPrice = formatCurrency(item.price * item.quantity);
      li.textContent = `${item.name} x${item.quantity} - ${formattedPrice} VND`;
      cartItemsList.appendChild(li);
    });

    // Cập nhật tổng số lượng và tổng giá trị
    document.getElementById('cart-count').textContent = data.total_items;
  });


document.addEventListener('DOMContentLoaded', function () {
  // Xử lý chuyển đổi giữa các modal
  const modals = {
    authModal: new bootstrap.Modal(document.getElementById('authModal')),
    forgotPasswordModal: new bootstrap.Modal(document.getElementById('forgotPasswordModal')),
    verifyOtpModal: new bootstrap.Modal(document.getElementById('verifyOtpModal')),
    resetPasswordModal: new bootstrap.Modal(document.getElementById('resetPasswordModal')),
    registerModal: new bootstrap.Modal(document.getElementById('registerModal')),
  };

  const forgotPasswordLink = document.getElementById('forgotPasswordLink');
  const registerLink = document.getElementById('registerLink');
  const sendOtpButton = document.getElementById('sendOtpBtn');
  const verifyOtpButton = document.getElementById('verifyOtpBtn');
  const resendOtpButton = document.getElementById('resendOtp');
  const otpInputs = document.querySelectorAll('.otp-input');

  // Chuyển từ Login → Forgot Password
  if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', function () {
      modals.authModal.hide();
      modals.forgotPasswordModal.show();
    });
  }

  // Chuyển từ Login → Register
  if (registerLink) {
    registerLink.addEventListener('click', function () {
      modals.authModal.hide();
      modals.registerModal.show();
    });
  }

  // Gửi mã OTP
  if (sendOtpButton) {
    sendOtpButton.addEventListener('click', function () {
      const email = document.getElementById('forgotEmail').value;
      fetch('/accounts/send-otp/', {
        method: 'POST',
        body: JSON.stringify({ email }),
        headers: { 'Content-Type': 'application/json' },
      })
        .then(response => response.json())
        .then(data => {
          alert(data.message);
          if (data.success) {
            modals.forgotPasswordModal.hide();
            modals.verifyOtpModal.show();
          }
        })
        .catch(error => console.error('Error:', error));
    });
  }

  // Chuyển focus giữa các ô OTP
  otpInputs.forEach((input, index) => {
    input.addEventListener('input', function () {
      if (this.value.length === 1 && index < otpInputs.length - 1) {
        otpInputs[index + 1].focus();
      }
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Backspace' && this.value.length === 0 && index > 0) {
        otpInputs[index - 1].focus();
      }
    });
  });

  // Xác minh OTP
  if (verifyOtpButton) {
    verifyOtpButton.addEventListener('click', function () {
      const otp = Array.from(otpInputs).map((input) => input.value).join('');
      fetch('/accounts/verify-otp/', {
        method: 'POST',
        body: JSON.stringify({ otp }),
        headers: { 'Content-Type': 'application/json' },
      })
        .then((response) => response.json())
        .then((data) => {
          alert(data.message);
          if (data.success) {
            modals.verifyOtpModal.hide();
            modals.resetPasswordModal.show();
          }
        })
        .catch((error) => console.error('Error:', error));
    });
  }

  // Gửi lại mã OTP
  if (resendOtpButton) {
    resendOtpButton.addEventListener('click', function () {
      const email = document.getElementById('forgotEmail').value;
      fetch('/accounts/resend-otp/', {
        method: 'POST',
        body: JSON.stringify({ email }),
        headers: { 'Content-Type': 'application/json' },
      })
        .then((response) => response.json())
        .then((data) => {
          alert(data.message);
        })
        .catch((error) => console.error('Error:', error));
    });
  }

  // Cập nhật hành động trong form
  function setAuthAction(action) {
    const actionInput = document.getElementById('action');
    const emailField = document.getElementById('emailField');
    const usernameField = document.getElementById('usernameField');
    const newPasswordField = document.getElementById('newPasswordField');

    actionInput.value = action;

    emailField.style.display = action === 'register' || action === 'forgot_password' ? 'block' : 'none';
    usernameField.style.display = action !== 'forgot_password' ? 'block' : 'none';
    newPasswordField.style.display = action === 'reset_password' ? 'block' : 'none';
  }

  // Xử lý gửi form auth
  const authForm = document.getElementById('authForm');
  if (authForm) {
    authForm.addEventListener('submit', function (event) {
      event.preventDefault();
      const formData = new FormData(this);

      fetch('/accounts/auth/', {
        method: 'POST',
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          alert(data.message);
          if (data.success) {
            location.reload();
          }
        })
        .catch((error) => console.error('Error:', error));
    });
  }
});
// Lấy CSRF Token từ thẻ meta
function getCsrfToken() {
  const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
  return csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
}

// Hàm hiển thị thông báo (dùng alert hoặc custom modal nếu cần)
function showAlert(message, type = 'info') {
  alert(`[${type.toUpperCase()}]: ${message}`);
}

// Gửi yêu cầu API
async function sendApiRequest(url, method, data = {}) {
  try {
    const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(data),
    });
    return await response.json();
  } catch (error) {
    console.error(`Error when sending API request to ${url}:`, error);
    showAlert('An error occurred. Please try again later.', 'error');
    return null;
  }
}

// Gửi OTP
const sendOtpButton = document.getElementById('sendOtpButton');
if (sendOtpButton) {
  sendOtpButton.addEventListener('click', async function () {
    const email = document.getElementById('forgotEmail').value;

    if (!email) {
      showAlert('Please enter your email.', 'warning');
      return;
    }

    const response = await sendApiRequest('/accounts/send-otp/', 'POST', { email });
    if (response && response.success) {
      showAlert(response.message, 'success');

      // Hiển thị modal xác minh OTP
      const forgotPasswordModal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById('forgotPasswordModal')
      );
      const verifyOtpModal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById('verifyOtpModal')
      );
      forgotPasswordModal.hide();
      verifyOtpModal.show();
    }
  });
}

// Xác minh OTP
const verifyOtpButton = document.getElementById('verifyOtpButton');
if (verifyOtpButton) {
  verifyOtpButton.addEventListener('click', async function () {
    const otp = document.getElementById('otpInput').value;

    if (!otp) {
      showAlert('Please enter the OTP sent to your email.', 'warning');
      return;
    }

    const response = await sendApiRequest('/accounts/verify-otp/', 'POST', { otp });
    if (response && response.success) {
      showAlert(response.message, 'success');

      // Đóng modal OTP và chuyển sang trang đặt lại mật khẩu
      const verifyOtpModal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById('verifyOtpModal')
      );
      verifyOtpModal.hide();
      window.location.href = '/accounts/reset-password/';
    }
  });
}

// Đặt lại mật khẩu
const resetPasswordButton = document.getElementById('resetPasswordButton');
if (resetPasswordButton) {
  resetPasswordButton.addEventListener('click', async function () {
    const password = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!password || !confirmPassword) {
      showAlert('Please fill in both password fields.', 'warning');
      return;
    }

    if (password !== confirmPassword) {
      showAlert('Passwords do not match.', 'error');
      return;
    }

    const response = await sendApiRequest('/accounts/reset-password/', 'POST', {
      password,
      confirmPassword,
    });
    if (response && response.success) {
      showAlert(response.message, 'success');
      window.location.href = '/accounts/login/';
    }
  });
}
