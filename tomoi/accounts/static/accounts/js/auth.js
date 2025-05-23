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
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: `email=${email}`
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


  // Gửi lại mã OTP
  if (resendOtpButton) {
    resendOtpButton.addEventListener('click', function () {
      const email = document.getElementById('forgotEmail').value;
      fetch('/accounts/resend-otp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: `email=${email}`
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
          if (data.success) {
            showNotification('Đăng nhập thành công! Bạn sẽ được chuyển hướng trong 5 giây.');
            setTimeout(() => location.reload(), 5000);
          } else {
            showNotification(data.message, 'error');
          }
        })
        .catch((error) => {
          console.error('Error:', error);
          showNotification('Có lỗi xảy ra khi đăng nhập. Vui lòng thử lại.', 'error');
        });
    });
  }
});

// Thêm hàm để lấy CSRF token
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split(';')
        .find(cookie => cookie.trim().startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}

// Sửa phần xử lý verify OTP
document.addEventListener('DOMContentLoaded', function() {
    const otpInputs = document.querySelectorAll('.otp-input');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');

    // Gom OTP và verify
    if (verifyOtpBtn) {
        verifyOtpBtn.addEventListener('click', async function() {
            const otp = Array.from(otpInputs)
                .map(input => input.value)
                .join('');

            try {
                const response = await fetch('/accounts/verify-otp/', {  // Sửa đường dẫn
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: JSON.stringify({ otp: otp })
                });

                const data = await response.json();
                if (data.success) {
                    // Nếu verify thành công
                    modals.verifyOtpModal.hide();
                    modals.resetPasswordModal.show();
                } else {
                    // Nếu verify thất bại
                    alert(data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi xác thực OTP');
            }
        });
    }

    // Xử lý hiển thị email trong modal verify OTP
    const displayEmail = document.getElementById('displayEmail');
    const editEmailLink = document.getElementById('editEmailLink');
    
    // Khi mở modal verify OTP, hiển thị email
    document.getElementById('verifyOtpModal').addEventListener('show.bs.modal', function () {
        const email = document.getElementById('forgotEmail').value;
        displayEmail.textContent = email;
    });

    // Xử lý khi click vào nút chỉnh sửa email
    editEmailLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Đóng modal verify OTP
        bootstrap.Modal.getInstance(document.getElementById('verifyOtpModal')).hide();
        
        // Mở lại modal quên mật khẩu
        bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal')).show();
        
        // Focus vào input email
        setTimeout(() => {
            document.getElementById('forgotEmail').focus();
        }, 500);
    });
});

// Lấy CSRF Token từ thẻ meta
function getCsrfToken() {
  const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
  return csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : '';
}

// Hàm hiển thị thông báo (dùng alert hoặc custom modal nếu cần)
function showNotification(message, type = 'success') {
  Swal.fire({
    text: message,
    icon: type,
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true
  });
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
    showNotification('An error occurred. Please try again later.', 'error');
    return null;
  }
}

// Gửi OTP
document.addEventListener('DOMContentLoaded', function () {
  const sendOtpBtn = document.getElementById('sendOtpBtn');
  const forgotPasswordForm = document.getElementById('forgotPasswordForm');
  const verifyOtpModal = new bootstrap.Modal(document.getElementById('verifyOtpModal'));

  sendOtpBtn.addEventListener('click', async function (e) {
    e.preventDefault();
    const email = document.getElementById('forgotEmail').value;

    try {
      const response = await fetch('/accounts/send-otp/', {  // Adjust URL to match your Django URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: `email=${email}`
      });

      const data = await response.json();

      if (data.success) {
        // Hide forgot password modal
        bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal')).hide();
        // Show OTP verification modal
        verifyOtpModal.show();
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Có lỗi xảy ra khi gửi OTP');
    }
  });
});

// Đặt lại mật khẩu
const resetPasswordButton = document.getElementById('resetPasswordButton');
if (resetPasswordButton) {
  resetPasswordButton.addEventListener('click', async function () {
    const password = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!password || !confirmPassword) {
      showNotification('Please fill in both password fields.', 'warning');
      return;
    }

    if (password !== confirmPassword) {
      showNotification('Passwords do not match.', 'error');
      return;
    }

    const response = await sendApiRequest('/store/reset-password/', 'POST', {
      password,
      confirmPassword,
    });
    if (response && response.success) {
      showNotification(response.message);
      window.location.href = '/store/login/';
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
  // OTP Input handling
  const otpInputs = document.querySelectorAll('.otp-input');
  otpInputs.forEach((input, index) => {
    input.addEventListener('input', function () {
      if (this.value.length === 1 && index < otpInputs.length - 1) {
        otpInputs[index + 1].focus();
      }
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Backspace' && !this.value && index > 0) {
        otpInputs[index - 1].focus();
      }
    });
  });

  // Verify OTP button click
  document.getElementById('verifyOtpBtn').addEventListener('click', async () => {
    const otp = Array.from(otpInputs).map(input => input.value).join('');

    try {
      const response = await fetch('/accounts/verify-otp/', {  // Sửa đường dẫn
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ otp })
      });

      const data = await response.json();
      if (data.success) {
        bootstrap.Modal.getInstance(document.getElementById('verifyOtpModal')).hide();
        bootstrap.Modal.getOrCreateInstance(document.getElementById('resetPasswordModal')).show();
      } else {
        alert(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Có lỗi xảy ra khi xác thực OTP');
    }
  });
});

function updateUserInfo(userData) {
  document.getElementById('userInfo').classList.remove('d-none');
  document.getElementById('balanceInfo').classList.remove('d-none');
  document.getElementById('rechargeBtn').classList.remove('d-none');
  document.getElementById('userAccountLink').classList.remove('d-none');
  document.getElementById('orderHistoryLink').classList.remove('d-none');
  document.getElementById('logoutLink').classList.remove('d-none');
}

// Giả sử bạn nhận được userData từ backend khi đăng nhập
fetch('/accounts/user-info/')
  .then((response) => response.json())
  .then((userData) => {
    if (userData.authenticated) {
      updateUserInfo(userData);
    }
  })

// đăng nhập
document.addEventListener('DOMContentLoaded', function () {
  // Login form handler
  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const response = await fetch(loginForm.action, {
      method: 'POST',
      body: new FormData(loginForm)
    });
    const data = await response.json();
    if (data.success) {
      location.reload();
    }
  });

  // OTP verification handler
  const verifyOtpBtn = document.getElementById('verifyOtpBtn');
  verifyOtpBtn.addEventListener('click', async () => {
    const otp = Array.from(document.querySelectorAll('.otp-input'))
      .map(input => input.value)
      .join('');

    const response = await fetch('/verify-otp/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: JSON.stringify({ otp })
    });

    const data = await response.json();
    if (data.success) {
      bootstrap.Modal.getInstance(document.getElementById('verifyOtpModal')).hide();
      bootstrap.Modal.getOrCreateInstance(document.querySelector(data.next_modal)).show();
    }
  });
});

// Đăng ký
document.addEventListener('DOMContentLoaded', function () {
  const registerForm = document.getElementById('registerForm');

  registerForm.addEventListener('submit', function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
            // Chuyển hướng đến trang xác thực
            window.location.href = data.redirect;
        } else {
            showNotification(data.error, 'error');
            if (data.action === 'login') {
                // Chuyển sang modal đăng nhập nếu email đã tồn tại
                bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
                bootstrap.Modal.getInstance(document.getElementById('authModal')).show();
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Có lỗi xảy ra khi đăng ký', 'error');
    });
  });
});

document.getElementById('registerForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const formData = new FormData(this);

  fetch('/accounts/register/', {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': formData.get('csrfmiddlewaretoken')
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showNotification(data.message);
        // Đóng modal đăng ký
        bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
      } else {
        showNotification(data.error, 'error');
        if (data.action === 'login') {
          // Chuyển sang modal đăng nhập nếu email đã tồn tại
          bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
          bootstrap.Modal.getInstance(document.getElementById('authModal')).show();
        }
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showNotification('Có lỗi xảy ra khi đăng ký', 'error');
    });
});

// Update auth state indicator
document.addEventListener('DOMContentLoaded', function () {
  const userIcon = document.querySelector('.nav-link.user-icon');
  if (document.querySelector('[data-user-authenticated="true"]')) {
    userIcon.classList.add('authenticated');
  }
});

document.addEventListener('DOMContentLoaded', function () {
  // Kiểm tra xem người dùng có thể truy cập /cart/api/
  fetch('/cart/api/')
    .then(response => {
      if (response.status === 401) {
        // Hiển thị modal login
        document.getElementById('authModal').style.display = 'block';
      } else {
        return response.json();
      }
    })
    .then(data => {
      console.log(data); // Xử lý phản hồi thành công
    })
    .catch(error => {
      console.error('Error:', error); // Xử lý lỗi khác
    });
});

// Thêm script để đếm ngược
document.addEventListener('DOMContentLoaded', function() {
    const resendBtn = document.getElementById('resendOtpBtn');
    let countdown = 30;
    let interval;
    let isCountingDown = false;  // Thêm biến để theo dõi trạng thái đếm ngược

    function updateButtonState() {
        if (isCountingDown) {
            resendBtn.disabled = true;
            resendBtn.style.color = '#6c757d';  // Màu xám
            resendBtn.style.cursor = 'not-allowed';
            resendBtn.textContent = `Gửi lại (${countdown} giây)`;
        } else {
            resendBtn.disabled = false;
            resendBtn.style.color = '#0d6efd';  // Màu xanh
            resendBtn.style.cursor = 'pointer';
            resendBtn.textContent = 'Gửi lại';
        }
    }

    function startCountdown() {
        isCountingDown = true;
        countdown = 30;
        updateButtonState();
        
        clearInterval(interval);
        interval = setInterval(function() {
            countdown--;
            if (countdown > 0) {
                updateButtonState();
            } else {
                clearInterval(interval);
                isCountingDown = false;
                updateButtonState();
            }
        }, 1000);
    }

    resendBtn.addEventListener('click', function() {
        if (isCountingDown) return;  // Không cho phép click khi đang đếm ngược
        
        const email = document.getElementById('forgotEmail').value;
        fetch('/accounts/resend-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: `email=${email}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                startCountdown();
                alert(data.message);
            } else {
                alert(data.error || 'Có lỗi xảy ra khi gửi lại OTP');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi gửi lại OTP');
        });
    });

    // Khởi động đếm ngược khi modal mở
    const verifyOtpModal = document.getElementById('verifyOtpModal');
    verifyOtpModal.addEventListener('shown.bs.modal', function () {
        startCountdown();
    });

    // Dọn dẹp interval khi modal đóng
    verifyOtpModal.addEventListener('hidden.bs.modal', function () {
        clearInterval(interval);
        isCountingDown = false;
        updateButtonState();
    });

    // Khởi tạo trạng thái ban đầu
    updateButtonState();
});

// Thêm hàm xử lý reset password thành công
function handleResetPasswordSuccess() {
    // Tạo và hiển thị popup
    const popup = document.createElement('div');
    popup.className = 'success-popup';
    popup.innerHTML = `
        <div class="popup-content">
            <i class="fas fa-check-circle"></i>
            <h4>Chúc mừng!</h4>
            <p>Bạn đã đổi mật khẩu thành công.</p>
        </div>
    `;
    document.body.appendChild(popup);

    // Thêm style cho popup
    const style = document.createElement('style');
    style.textContent = `
        .success-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1100;
            text-align: center;
        }
        .popup-content i {
            color: #28a745;
            font-size: 48px;
            margin-bottom: 15px;
        }
        .popup-content h4 {
            margin-bottom: 10px;
            color: #333;
        }
        .popup-content p {
            color: #666;
        }
    `;
    document.head.appendChild(style);

    // Đóng modal reset password
    bootstrap.Modal.getInstance(document.getElementById('resetPasswordModal')).hide();

    // Sau 5 giây, xóa popup và chuyển hướng
    setTimeout(() => {
        document.body.removeChild(popup);
        window.location.href = '/';  // Chuyển về trang chủ
    }, 5000);
}

// Cập nhật xử lý form reset password
document.getElementById('resetPasswordForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    try {
        const formData = new FormData(this);
        const response = await fetch('/accounts/reset-password/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            handleResetPasswordSuccess();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi đặt lại mật khẩu');
    }
});

// Sử dụng trong các hàm callback
function handleResponse(response) {
    if (response.success) {
        showNotification(response.message);
        // Xử lý thành công...
    } else {
        showNotification(response.message, 'error');
        // Xử lý thất bại...
    }
}