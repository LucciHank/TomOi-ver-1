document.addEventListener('DOMContentLoaded', function() {
    console.log('Security.js initialized');

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
            const method = document.getElementById('fa_method')?.value;
            
            if (!method) {
                Swal.fire('Lỗi', 'Vui lòng chọn phương thức xác thực', 'error');
                return;
            }

            if (method === 'email') {
                try {
                    // Hiển thị loading
                    Swal.fire({
                        title: 'Đang gửi mã OTP',
                        html: 'Vui lòng đợi trong giây lát...',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });

                    const response = await fetch('/accounts/security/send-otp-email/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const data = await response.json();
                    
                    // Đóng loading
                    Swal.close();

                    if (data.status === 'success') {
                        // Đóng modal setup
                        const setup2FAModal = bootstrap.Modal.getInstance(document.getElementById('setup2FAModal'));
                        setup2FAModal.hide();

                        // Hiển thị thông báo thành công
                        await Swal.fire({
                            icon: 'success',
                            iconColor: '#28a745', // Màu xanh lá
                            title: 'Đã gửi mã OTP thành công',
                            text: 'Vui lòng kiểm tra email của bạn',
                            timer: 2000,
                            showConfirmButton: false,
                            customClass: {
                                popup: 'animated fadeInDown faster'
                            }
                        });

                        // Mở modal verify OTP
                        const verifyOTPModal = new bootstrap.Modal(document.getElementById('verifyOTPModal'));
                        verifyOTPModal.show();

                        // Focus vào ô OTP đầu tiên
                        setTimeout(() => {
                            document.querySelector('.otp-input')?.focus();
                        }, 500);
                    } else {
                        throw new Error(data.message);
                    }
                } catch (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: error.message || 'Không thể gửi mã OTP'
                    });
                }
            } else {
                try {
                    let response;
                    switch (method) {
                        case 'password':
                            const password = document.getElementById('setup_2fa_password')?.value;
                            const confirmPassword = document.getElementById('setup_2fa_confirm')?.value;
                            
                            // Kiểm tra mật khẩu
                            if (!password) {
                                Swal.fire('Lỗi', 'Vui lòng nhập mật khẩu', 'error');
                                return;
                            }

                            if (password !== confirmPassword) {
                                Swal.fire('Lỗi', 'Mật khẩu không khớp', 'error');
                                return;
                            }

                            response = await fetch('/accounts/security/setup-2fa/', {
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
                    if (data.status === 'success') {
                        if (method === 'email') {
                            // Hiển thị form nhập OTP
                            document.getElementById('otpSection')?.classList.remove('d-none');
                            if (typeof startCountdown === 'function') {
                                startCountdown();
                            }
                        }
                        
                        Swal.fire({
                            icon: 'success',
                            title: 'Thành công',
                            text: data.message
                        });
                    } else {
                        throw new Error(data.message);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: error.message || 'Có lỗi xảy ra, vui lòng thử lại'
                    });
                }
            }
        });
    }

    // Xử lý form tạo mật khẩu cấp 2
    const password2FAForm = document.getElementById('password2FAForm');
    if (password2FAForm) {
        password2FAForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const passwordInput = document.getElementById('fa_password');
            const confirmInput = document.getElementById('fa_password_confirm');
            
            if (!passwordInput || !confirmInput) {
                console.error('Không tìm thấy trường input');
                return;
            }

            const password = passwordInput.value;
            const confirmPassword = confirmInput.value;

            // Kiểm tra mật khẩu
            if (password.length < 6) {
                Swal.fire('Lỗi', 'Mật khẩu phải có ít nhất 6 ký tự', 'error');
                return;
            }

            if (!/\d/.test(password)) {
                Swal.fire('Lỗi', 'Mật khẩu phải chứa ít nhất 1 số', 'error');
                return;
            }

            if (password !== confirmPassword) {
                Swal.fire('Lỗi', 'Mật khẩu xác nhận không khớp', 'error');
                return;
            }

            try {
                const response = await fetch('/accounts/security/setup-2fa/', {
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

                const data = await response.json();
                
                if (data.status === 'success') {
                    // Đóng modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('password2FAModal'));
                    if (modal) {
                        modal.hide();
                    }

                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công!',
                        text: 'Đã thiết lập mật khẩu cấp 2',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    throw new Error(data.message || 'Có lỗi xảy ra');
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire('Lỗi', error.message, 'error');
            }
        });
    }

    // Hàm đếm ngược cho OTP
    function startCountdown() {
        const countdownEl = document.getElementById('countdown');
        if (!countdownEl) return;

        let timeLeft = 60;
        countdownEl.textContent = timeLeft;

        const timer = setInterval(() => {
            timeLeft--;
            if (countdownEl) {
                countdownEl.textContent = timeLeft;
            }

            if (timeLeft <= 0) {
                clearInterval(timer);
                const resendBtn = document.getElementById('resendOtpBtn');
                if (resendBtn) {
                    resendBtn.disabled = false;
                }
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

    // Xử lý nút đổi mật khẩu cấp 2
    document.addEventListener('click', function(e) {
        // Nút đổi mật khẩu cấp 2
        if (e.target.matches('#change2FABtn') || e.target.closest('#change2FABtn')) {
            const modal = new bootstrap.Modal(document.getElementById('change2FAPasswordModal'));
            modal.show();
        }

        // Nút xác nhận thiết bị
        if (e.target.matches('.confirm-device-btn')) {
            const loginId = e.target.dataset.loginId;
            confirmDevice(loginId);
        }

        // Nút "Không phải tôi"
        if (e.target.matches('.logout-device-btn')) {
            const loginId = e.target.dataset.loginId;
            logoutDevice(loginId);
        }
    });

    // Xử lý form đổi mật khẩu
    document.getElementById('changePasswordForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const form = e.target;
        const currentPassword = form.querySelector('input[name="current_password"]').value;
        const newPassword = form.querySelector('input[name="new_password"]').value;
        const confirmPassword = form.querySelector('input[name="confirm_password"]').value;

        // Kiểm tra mật khẩu mới và xác nhận mật khẩu
        if (newPassword !== confirmPassword) {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: 'Mật khẩu mới và xác nhận mật khẩu không khớp'
            });
            return;
        }

        try {
            const response = await fetch('/accounts/security/change-password/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công',
                    text: 'Đổi mật khẩu thành công',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    window.location.reload();
                });
            } else {
                if (data.error === 'current_password_incorrect') {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Mật khẩu hiện tại không đúng'
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: data.message || 'Có lỗi xảy ra'
                    });
                }
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: 'Có lỗi xảy ra, vui lòng thử lại sau'
            });
        }
    });

    // Thêm xử lý realtime validation
    document.getElementById('new_password')?.addEventListener('input', function() {
        const password = this.value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        // Kiểm tra độ dài
        const lengthValid = password.length >= 8;
        const lengthCheck = document.getElementById('length-check');
        lengthCheck.classList.remove('text-success');
        if (lengthValid) {
            lengthCheck.classList.add('text-success');
        }
        
        // Kiểm tra số hoặc chữ hoa
        const numberOrUpperValid = /\d/.test(password) || /[A-Z]/.test(password);
        const numberOrUpperCheck = document.getElementById('number-or-upper-check');
        numberOrUpperCheck.classList.remove('text-success');
        if (numberOrUpperValid) {
            numberOrUpperCheck.classList.add('text-success');
        }
        
        // Kiểm tra ký tự đặc biệt
        const specialCharValid = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        const specialCharCheck = document.getElementById('special-char-check');
        specialCharCheck.classList.remove('text-success');
        if (specialCharValid) {
            specialCharCheck.classList.add('text-success');
        }
        
        // Kiểm tra khớp mật khẩu
        const matchValid = password === confirmPassword;
        const matchCheck = document.getElementById('match-check');
        matchCheck.classList.remove('text-success');
        if (matchValid) {
            matchCheck.classList.add('text-success');
        }
    });

    document.getElementById('confirm_password')?.addEventListener('input', function() {
        const password = document.getElementById('new_password').value;
        const confirmPassword = this.value;
        
        // Kiểm tra khớp mật khẩu
        document.getElementById('match-check').classList.toggle('text-success', password === confirmPassword);
    });

    // Thêm xử lý cho nút xóa mật khẩu cấp 2
    document.addEventListener('click', async function(e) {
        if (e.target.matches('#delete2FABtn') || e.target.closest('#delete2FABtn')) {
            // Hiển thị dialog xác nhận
            const result = await Swal.fire({
                title: 'Xác nhận xóa',
                text: 'Bạn có chắc chắn muốn xóa mật khẩu cấp 2?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Xóa',
                cancelButtonText: 'Hủy'
            });

            if (result.isConfirmed) {
                try {
                    const response = await fetch('/accounts/security/delete-2fa/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const data = await response.json();

                    if (response.ok) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Thành công',
                            text: 'Đã xóa mật khẩu cấp 2',
                            showConfirmButton: false,
                            timer: 1500
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        throw new Error(data.message || 'Có lỗi xảy ra');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: error.message || 'Có lỗi xảy ra, vui lòng thử lại'
                    });
                }
            }
        }
    });

    // Xử lý nút gửi lại OTP
    document.getElementById('resendOtpBtn')?.addEventListener('click', async function() {
        if (this.disabled) return;
        
        try {
            // Hiển thị loading
            Swal.fire({
                title: 'Đang gửi lại mã OTP',
                html: 'Vui lòng đợi trong giây lát...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            const response = await fetch('/accounts/security/send-otp-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();
            Swal.close();

            if (data.status === 'success') {
                // Reset countdown
                this.disabled = true;
                let timeLeft = 60;
                const countdownEl = document.getElementById('countdown');
                countdownEl.textContent = timeLeft;

                const timer = setInterval(() => {
                    timeLeft--;
                    if (countdownEl) {
                        countdownEl.textContent = timeLeft;
                    }
                    if (timeLeft <= 0) {
                        clearInterval(timer);
                        this.disabled = false;
                    }
                }, 1000);

                // Thông báo thành công
                Swal.fire({
                    icon: 'success',
                    iconColor: '#28a745',
                    title: 'Đã gửi lại mã OTP',
                    text: 'Vui lòng kiểm tra email của bạn',
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: error.message || 'Không thể gửi lại mã OTP'
            });
        }
    });
});

// Thêm hàm handle2FAMethodChange
function handle2FAMethodChange() {
    const method = document.getElementById('fa_method').value;
    const submitBtn = document.getElementById('setup2FASubmitBtn');
    
    // Ẩn tất cả các trường
    document.getElementById('fa_password_fields')?.classList.add('d-none');
    document.getElementById('fa_email_fields')?.classList.add('d-none');
    document.getElementById('fa_google_fields')?.classList.add('d-none');
    
    // Hiển thị trường tương ứng
    if (method) {
        const fields = document.getElementById(`fa_${method}_fields`);
        if (fields) {
            fields.classList.remove('d-none');
        }
        
        // Thay đổi text nút submit
        if (submitBtn) {
            submitBtn.textContent = method === 'email' ? 'Gửi mã OTP' : 'Lưu thay đổi';
        }
    }
}

// Xử lý OTP input
document.querySelectorAll('.otp-input').forEach(input => {
    input.addEventListener('keyup', function(e) {
        if (this.value.length === 1) {
            this.classList.add('filled');
            const next = this.nextElementSibling;
            if (next && next.classList.contains('otp-input')) {
                next.focus();
            }
        } else {
            this.classList.remove('filled');
        }

        // Cập nhật giá trị OTP tổng
        const otpValue = Array.from(document.querySelectorAll('.otp-input'))
            .map(input => input.value)
            .join('');
        document.getElementById('otpValue').value = otpValue;
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && !this.value) {
            const prev = this.previousElementSibling;
            if (prev && prev.classList.contains('otp-input')) {
                prev.focus();
            }
        }
    });
});

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

// Hàm xác nhận thiết bị
async function confirmDevice(loginId) {
    try {
        // Hiện modal xác nhận mật khẩu cấp 2
        const { value: password } = await Swal.fire({
            title: 'Xác nhận mật khẩu cấp 2',
            input: 'password',
            inputLabel: 'Vui lòng nhập mật khẩu cấp 2 để xác nhận thiết bị',
            inputPlaceholder: 'Nhập mật khẩu cấp 2',
            showCancelButton: true,
            cancelButtonText: 'Hủy',
            confirmButtonText: 'Xác nhận',
            inputValidator: (value) => {
                if (!value) {
                    return 'Vui lòng nhập mật khẩu cấp 2!';
                }
            }
        });

        if (password) {
            const response = await fetch('/accounts/confirm-device/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    login_id: loginId,
                    password: password 
                })
            });

            if (!response.ok) {
                throw new Error('Lỗi kết nối server');
            }

            const data = await response.json();
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công!',
                    text: 'Đã xác nhận thiết bị',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    window.location.reload();
                });
            } else {
                throw new Error(data.message || 'Có lỗi xảy ra');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire('Lỗi', error.message, 'error');
    }
}

// Hàm đăng xuất thiết bị
async function logoutDevice(loginId) {
    try {
        // Hiện modal xác nhận mật khẩu cấp 2
        const { value: password } = await Swal.fire({
            title: 'Xác nhận mật khẩu cấp 2',
            input: 'password',
            inputLabel: 'Vui lòng nhập mật khẩu cấp 2 để đăng xuất thiết bị',
            inputPlaceholder: 'Nhập mật khẩu cấp 2',
            showCancelButton: true,
            cancelButtonText: 'Hủy',
            confirmButtonText: 'Xác nhận',
            inputValidator: (value) => {
                if (!value) {
                    return 'Vui lòng nhập mật khẩu cấp 2!';
                }
            }
        });

        if (password) {
            const response = await fetch('/accounts/logout-device/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    login_id: loginId,
                    password: password 
                })
            });

            const data = await response.json();
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công!',
                    text: 'Đã đăng xuất thiết bị',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    window.location.reload();
                });
            } else {
                throw new Error(data.message || 'Có lỗi xảy ra');
            }
        }
    } catch (error) {
        Swal.fire('Lỗi', error.message, 'error');
    }
}

// Xử lý verify OTP
document.getElementById('verifyOTPForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const otp = document.getElementById('otpValue').value;

    if (otp.length !== 6) {
        Swal.fire('Lỗi', 'Vui lòng nhập đủ 6 số OTP', 'error');
        return;
    }

    try {
        const response = await fetch('/accounts/security/verify-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ otp })
        });

        const data = await response.json();
        if (data.status === 'success') {
            // Đóng modal verify OTP
            const verifyOTPModal = bootstrap.Modal.getInstance(document.getElementById('verifyOTPModal'));
            verifyOTPModal.hide();

            // Hiển thị thông báo thành công
            Swal.fire({
                icon: 'success',
                title: 'Thành công',
                text: 'Đặt mật khẩu cấp 2 thành công',
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                window.location.reload();
            });
        } else {
            throw new Error(data.message);
        }
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Lỗi',
            text: error.message || 'Mã OTP không chính xác'
        });
    }
});



