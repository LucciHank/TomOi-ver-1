document.addEventListener('DOMContentLoaded', function() {
    // Xử lý nút "Tạo mật khẩu cấp 2"
    const setup2FABtn = document.getElementById('setup2FABtn');
    if (setup2FABtn) {
        setup2FABtn.addEventListener('click', function() {
            const setup2FAModal = new bootstrap.Modal(document.getElementById('setup2FAModal'));
            setup2FAModal.show();
        });
    }

    // Xử lý khi chọn phương thức xác thực
    const faMethodSelect = document.getElementById('fa_method');
    if (faMethodSelect) {
        faMethodSelect.addEventListener('change', handle2FAMethodChange);
    }

    // Xử lý form setup 2FA
        const setup2FAForm = document.getElementById('setup2FAForm');
    if (setup2FAForm) {
        setup2FAForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const method = document.getElementById('fa_method').value;
            
            if (!method) {
                Swal.fire('Lỗi', 'Vui lòng chọn phương thức xác thực', 'error');
                return;
            }

            try {
                let response;
            switch (method) {
                case 'password':
                        const password = document.getElementById('setup_2fa_password').value;
                        const confirmPassword = document.getElementById('setup_2fa_password_confirm').value;
                        
                        if (password !== confirmPassword) {
                            Swal.fire('Lỗi', 'Mật khẩu xác nhận không khớp', 'error');
                            return;
                        }
                        
                        response = await fetch('/accounts/setup-2fa/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({
                                method: 'password',
                                password: password
                            })
                        });
                        break;

                    case 'email':
                        const otp = document.querySelector('#fa_email_fields input[name="otp"]').value;
                        response = await fetch('/accounts/setup-2fa/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({
                                method: 'email',
                                otp: otp
                            })
                        });
                        break;

                    case 'google':
                        const gaOtp = document.getElementById('gaOtpInput').value;
                        response = await fetch('/accounts/verify-ga/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                            body: JSON.stringify({
                                otp: gaOtp
                            })
            });
                        break;
                }

            const data = await response.json();
                if (data.success || data.status === 'success') {
                    await Swal.fire({
                    icon: 'success',
                    title: 'Thành công',
                    text: 'Đã thiết lập xác thực 2 lớp thành công',
                    timer: 1500,
                    showConfirmButton: false
                });
                
                    // Đóng modal và cập nhật UI
                    bootstrap.Modal.getInstance(document.getElementById('setup2FAModal')).hide();
                    updateUI2FAStatus(method);
            } else {
                    throw new Error(data.message || 'Có lỗi xảy ra');
            }
        } catch (error) {
            Swal.fire('Lỗi', error.message, 'error');
        }
        });
    }

    // Hàm đếm ngược cho OTP
    function startCountdown() {
        const countdownEl = document.getElementById('setup_countdown_timer');
        const resendBtn = document.getElementById('setup_resend_otp_btn');
        if (!countdownEl || !resendBtn) return;

        let timeLeft = 60;
        resendBtn.disabled = true;

        const timer = setInterval(() => {
            timeLeft--;
            countdownEl.textContent = timeLeft;

            if (timeLeft <= 0) {
                clearInterval(timer);
                resendBtn.disabled = false;
            }
        }, 1000);
    }

    // Hàm cập nhật UI sau khi setup 2FA
    function updateUI2FAStatus(method) {
        const container = document.querySelector('.section-content');
        if (!container) return;

        const methodNames = {
            'password': 'Tự tạo mật khẩu',
            'email': 'OTP qua email',
            'google': 'Google Authenticator'
        };

        const template = `
            <p>Bạn đã thiết lập mật khẩu cấp 2 với phương thức: <strong>${methodNames[method]}</strong></p>
            <div class="mt-3">
                <button type="button" class="btn btn-primary me-2" id="change2FABtn">
                    <i class="fas fa-key me-2"></i>Đổi mật khẩu cấp 2
                </button>
                <button type="button" class="btn btn-outline-danger" id="delete2FABtn">
                    <i class="fas fa-trash-alt me-2"></i>Xóa mật khẩu cấp 2
                </button>
            </div>
        `;

        container.innerHTML = template;
    }

    console.log('Security.js initialized');
});

// Thêm hàm handle2FAMethodChange
function handle2FAMethodChange() {
    const method = document.getElementById('fa_method').value;
    
    // Ẩn tất cả các trường
    document.getElementById('fa_password_fields')?.classList.add('d-none');
    document.getElementById('fa_email_fields')?.classList.add('d-none');
    document.getElementById('fa_google_fields')?.classList.add('d-none');
    
    // Hiển thị trường tương ứng
    if (method) {
        document.getElementById(`fa_${method}_fields`)?.classList.remove('d-none');
        
        if (method === 'google') {
            // Tạo QR code cho Google Authenticator
            fetch('/accounts/security/setup-ga/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Hiển thị QR code và secret key
                    const qrContainer = document.getElementById('fa_google_fields');
                    qrContainer.innerHTML = `
                        <div class="text-center mb-4">
                            <img src="${data.qr_code}" alt="QR Code" class="qr-code mb-3">
                            <div class="secret-key-container">
                                <p class="mb-2">Mã bí mật của bạn:</p>
                                <div class="d-flex align-items-center justify-content-center gap-2">
                                    <code id="gaSecretKey">${data.secret}</code>
                                    <button type="button" class="btn btn-sm btn-outline-secondary copy-btn" 
                                            onclick="navigator.clipboard.writeText('${data.secret}')">
                                        <i class="fas fa-copy"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Nhập mã xác thực từ ứng dụng</label>
                            <input type="text" class="form-control" id="gaOtpInput" 
                                   maxlength="6" placeholder="Nhập mã 6 số">
                        </div>
                    `;
                }
            });
        }
        
        if (method === 'email') {
            // Gửi OTP qua email
            fetch('/accounts/security/send-otp-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startCountdown();
                }
            });
        }
    }
}



