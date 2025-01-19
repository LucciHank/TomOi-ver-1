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
        fetch('/store/send-otp/', {
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
  
  
    // Gửi lại mã OTP
    if (resendOtpButton) {
      resendOtpButton.addEventListener('click', function () {
        const email = document.getElementById('forgotEmail').value;
        fetch('/store/resend-otp/', {
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
            if (data.success) {
              showAlert('Đăng nhập thành công! Bạn sẽ được chuyển hướng trong 5 giây.', 'success');
              setTimeout(() => location.reload(), 5000);
            } else {
              showAlert(data.message, 'error');
            }
          })
          .catch((error) => {
            console.error('Error:', error);
            showAlert('Có lỗi xảy ra khi đăng nhập. Vui lòng thử lại.', 'error');
          });
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
  document.addEventListener('DOMContentLoaded', function() {
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    const forgotPasswordForm = document.getElementById('forgotPasswordForm');
    const verifyOtpModal = new bootstrap.Modal(document.getElementById('verifyOtpModal'));
    
    sendOtpBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        const email = document.getElementById('forgotEmail').value;
        
        try {
            const response = await fetch('/send-otp/', {  // Adjust URL to match your Django URL
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
        window.location.href = '/store/reset-password/';
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
  
      const response = await sendApiRequest('/store/reset-password/', 'POST', {
        password,
        confirmPassword,
      });
      if (response && response.success) {
        showAlert(response.message, 'success');
        window.location.href = '/store/login/';
      }
    });
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    // OTP Input handling
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', function() {
            if (this.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
    });

    // Verify OTP button click
    document.getElementById('verifyOtpBtn').addEventListener('click', function() {
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        fetch('/accounts/verify-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ otp: otp })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Hide OTP modal and show reset password modal
                bootstrap.Modal.getInstance(document.getElementById('verifyOtpModal')).hide();
                bootstrap.Modal.getOrCreateInstance(document.getElementById('resetPasswordModal')).show();
            } else {
                alert('Mã OTP không hợp lệ. Vui lòng thử lại.');
            }
        });
    });
});

 // Verify OTP button click
 document.getElementById('verifyOtpBtn').addEventListener('click', function() {
    const otp = Array.from(otpInputs).map(input => input.value).join('');
    
    fetch('/accounts/verify-otp/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ otp: otp })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Hide OTP modal and show reset password modal
            bootstrap.Modal.getInstance(document.getElementById('verifyOtpModal')).hide();
            bootstrap.Modal.getOrCreateInstance(document.getElementById('resetPasswordModal')).show();
        } else {
            alert('Mã OTP không hợp lệ. Vui lòng thử lại.');
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
    document.addEventListener('DOMContentLoaded', function() {
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
      document.addEventListener('DOMContentLoaded', function() {
        const registerForm = document.getElementById('registerForm');
        
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log("Form submitted");
            
            const formData = new FormData(this);
            
            fetch('/store/register/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(res => res.json())
            .then(data => {
                console.log("Response:", data);
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    if (data.error === 'Email đã tồn tại!') {
                        if (confirm(data.error + '\nĐăng nhập ngay?')) {
                            bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
                            bootstrap.Modal.getOrCreateInstance(document.getElementById('authModal')).show();
                        }
                    } else {
                        alert(data.error);
                    }
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert('Có lỗi xảy ra khi đăng ký');
            });
        });
    });
  
    document.getElementById('registerForm').addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      
      fetch('/store/register/', {
          method: 'POST',
          body: formData,
          headers: {
              'X-CSRFToken': formData.get('csrfmiddlewaretoken')
          }
      })
      .then(res => res.json())
      .then(data => {
          if (data.success) {
              window.location.href = data.redirect;
          } else {
              alert(data.error);
          }
      });
  });