document.addEventListener('DOMContentLoaded', function() {
    console.log('Security.js initialized');

    // Khởi tạo modal với kiểm tra null
    const initializeModal = (id) => {
        const element = document.getElementById(id);
        return element ? new bootstrap.Modal(element) : null;
    };

    // Danh sách modal
    const modals = {
        setup2FA: initializeModal('setup2FAModal'),
        verify2FA: initializeModal('verify2FAModal'),
        verifyOTP: initializeModal('verifyOTPModal'),
        verifyGA: initializeModal('verifyGAModal'),
        edit2FASettings: initializeModal('edit2FASettingsModal'),
        change2FAPassword: initializeModal('change2FAPasswordModal')
    };

    // Kiểm tra toggle password
    const initPasswordToggles = () => {
        document.querySelectorAll('.toggle-password').forEach(icon => {
            icon.addEventListener('click', function() {
                const input = this.previousElementSibling;
                if (!input) return;
                
                const type = input.type === 'password' ? 'text' : 'password';
                input.type = type;
                this.classList.toggle('fa-eye-slash');
            });
        });
    };

    // Xử lý sự kiện modal
    const initModalTriggers = () => {
        // Setup 2FA
        document.getElementById('setup2FABtn')?.addEventListener('click', (e) => {
            e.preventDefault();
            modals.setup2FA?.show();
        });

        // Change 2FA Method
        document.getElementById('change2FAMethodBtn')?.addEventListener('click', (e) => {
            e.preventDefault();
            modals.setup2FA?.show();
        });

        // Edit 2FA Settings
        document.getElementById('edit2FASettingsBtn')?.addEventListener('click', (e) => {
            e.preventDefault();
            modals.edit2FASettings?.show();
        });

        // Delete 2FA
        document.getElementById('delete2FABtn')?.addEventListener('click', async (e) => {
            e.preventDefault();
            const result = await Swal.fire({
                title: 'Xác nhận xóa?',
                text: "Bạn không thể hoàn tác hành động này!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Xóa!'
            });

            if (result.isConfirmed) {
                try {
                    const response = await fetch('/accounts/security/delete-2fa/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                            'Content-Type': 'application/json'
                        }
                    });

                    const data = await response.json();
                    if (data.status === 'success') {
                        Swal.fire('Đã xóa!', data.message, 'success').then(() => window.location.reload());
                    }
                } catch (error) {
                    Swal.fire('Lỗi!', error.message || 'Có lỗi xảy ra', 'error');
                }
            }
        });
    };

    // Xử lý form setup 2FA
    const init2FASetupForm = () => {
        const form = document.getElementById('setup2FAForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Validate client-side
            const method = document.getElementById('2fa_method').value;
            const password = document.getElementById('2fa_password')?.value;
            const confirmPassword = document.getElementById('2fa_password_confirm')?.value;

            if (method === 'password') {
                if (!password || !confirmPassword) {
                    Swal.fire('Lỗi!', 'Vui lòng điền đầy đủ mật khẩu', 'error');
                    return;
                }
                
                if (password !== confirmPassword) {
                    Swal.fire('Lỗi!', 'Mật khẩu xác nhận không khớp', 'error');
                    return;
                }

                if (password.length < 6) {
                    Swal.fire('Lỗi!', 'Mật khẩu phải có ít nhất 6 ký tự', 'error');
                    return;
                }
            }

            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

            try {
                if (!csrfToken) throw new Error('Missing CSRF token');
                
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken.value
                    }
                });

                const data = await response.json();
                
                if (!response.ok) throw new Error(data.message || `HTTP error! status: ${response.status}`);

                if (data.status === 'success') {
                    Swal.fire('Thành công!', data.message, 'success').then(() => {
                        window.location.reload();
                    });
                } else {
                    const errorMessage = data.errors 
                        ? Object.values(data.errors).join('\n')
                        : data.message || 'Lỗi không xác định';
                        
                    Swal.fire('Lỗi!', errorMessage, 'error');
                }
            } catch (error) {
                console.error('Submission error:', error);
                Swal.fire('Lỗi!', error.message || 'Lỗi kết nối đến server', 'error');
            }
        });
    };

    // Xử lý thay đổi phương thức 2FA
    window.handle2FAMethodChange = function() {
        const method = document.getElementById('2fa_method')?.value;
        const passwordFields = document.getElementById('2fa_password_fields');
        const emailFields = document.getElementById('2fa_email_fields');
        const googleFields = document.getElementById('2fa_google_fields');

        // Ẩn tất cả các trường
        [passwordFields, emailFields, googleFields].forEach(field => {
            if (field) field.classList.add('d-none');
        });

        // Hiển thị trường tương ứng
        if (method === 'password' && passwordFields) {
            passwordFields.classList.remove('d-none');
        } else if (method === 'email' && emailFields) {
            emailFields.classList.remove('d-none');
        } else if (method === 'google_authenticator' && googleFields) {
            googleFields.classList.remove('d-none');
            setupGoogleAuthenticator();
        }
    };

    // Xử lý Google Authenticator
    async function setupGoogleAuthenticator() {
        try {
            const response = await fetch('/accounts/security/setup-ga/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();
            if (data.status === 'success') {
                const qrCode = document.getElementById('gaQrCode');
                const secretKey = document.getElementById('gaSecretKey');
                if (qrCode) qrCode.src = data.qr_code;
                if (secretKey) secretKey.textContent = data.secret;

                // Xử lý input OTP
                const otpInput = document.getElementById('gaOtpInput');
                if (otpInput) {
                    otpInput.addEventListener('input', async function() {
                        if (this.value.length === 6) {
                            try {
                                const verifyResponse = await fetch('/accounts/security/verify-ga/', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                    },
                                    body: JSON.stringify({
                                        otp: this.value
                                    })
                                });

                                const verifyData = await verifyResponse.json();
                                if (verifyData.status === 'success') {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Thành công',
                                        text: 'Cài đặt Google Authenticator thành công'
                                    }).then(() => {
                                        window.location.reload();
                                    });
                                } else {
                                    this.value = '';
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Lỗi',
                                        text: 'Mã xác thực không đúng, vui lòng thử lại'
                                    });
                                }
                            } catch (error) {
                                console.error('Error:', error);
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Lỗi',
                                    text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                                });
                            }
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: 'Đã có lỗi xảy ra khi thiết lập Google Authenticator'
            });
        }
    }

    // Khởi động tất cả chức năng
    const initializeAll = () => {
        initPasswordToggles();
        initModalTriggers();
        init2FASetupForm();
        initGoogleAuthenticator();
    };

    initializeAll();
});

// Xử lý sự kiện cho nút Đổi và Xóa mật khẩu cấp 2
document.getElementById('change_password_btn').addEventListener('click', function () {
    alert('Chức năng đổi mật khẩu cấp 2 đang được xử lý.');
});

document.getElementById('delete_password_btn').addEventListener('click', function () {
    alert('Chức năng xóa mật khẩu cấp 2 đang được xử lý.');
});

