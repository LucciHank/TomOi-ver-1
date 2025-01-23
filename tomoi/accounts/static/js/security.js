document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo tất cả các modal
    const modals = {
        setup2FA: new bootstrap.Modal(document.getElementById('setup2FAModal')),
        verify2FA: new bootstrap.Modal(document.getElementById('verify2FAModal')),
        verifyOTP: new bootstrap.Modal(document.getElementById('verifyOTPModal')),
        verifyGA: new bootstrap.Modal(document.getElementById('verifyGAModal')),
        edit2FASettings: new bootstrap.Modal(document.getElementById('edit2FASettingsModal')),
        change2FAPassword: new bootstrap.Modal(document.getElementById('change2FAPasswordModal'))
    };

    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    });

    // Setup 2FA modal
    const setup2FABtn = document.getElementById('setup2FABtn');
    const setup2FAModal = new bootstrap.Modal(document.getElementById('setup2FAModal'));

    if (setup2FABtn) {
        setup2FABtn.addEventListener('click', () => {
            setup2FAModal.show();
        });
    }

    // Handle 2FA method selection
    document.querySelectorAll('input[name="2fa_method"]').forEach(radio => {
        radio.addEventListener('change', function() {
            // Hide all method fields
            document.querySelectorAll('.2fa-method-fields').forEach(field => {
                field.classList.add('d-none');
            });
            
            // Show selected method fields
            const selectedField = document.getElementById(`${this.id}_fields`);
            if (selectedField) {
                selectedField.classList.remove('d-none');
            }
        });
    });

    // Form submission handling
    const setup2FAForm = document.getElementById('setup2FAForm');
    if (setup2FAForm) {
        setup2FAForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/accounts/security/setup-2fa/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: data.message
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: data.message
                    });
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        });
    }

    // Password toggle functionality
    window.togglePassword = function(button) {
        const input = button.closest('.position-relative').querySelector('input');
        const icon = button.querySelector('i');
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        
        input.setAttribute('type', type);
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    };

    // Xử lý khi chọn phương thức xác thực
    function handle2FAMethodChange() {
        const selectedMethod = document.getElementById('2fa_method').value;
        const passwordFields = document.getElementById('2fa_password_fields');
        const emailFields = document.getElementById('2fa_email_fields');
        const googleFields = document.getElementById('2fa_google_fields');

        // Ẩn tất cả các trường
        [passwordFields, emailFields, googleFields].forEach(field => {
            if (field) field.classList.add('d-none');
        });

        // Hiển thị trường tương ứng
        if (selectedMethod === 'password') {
            passwordFields.classList.remove('d-none');
            // Reset form khi chuyển method
            document.getElementById('2fa_password').value = '';
            document.getElementById('2fa_password_confirm').value = '';
        } else if (selectedMethod === 'email') {
            emailFields.classList.remove('d-none');
        } else if (selectedMethod === 'google_authenticator') {
            googleFields.classList.remove('d-none');
        }
    }

    // Xử lý đổi mật khẩu cấp 2
    const change2FABtn = document.getElementById('change2FABtn');
    if (change2FABtn) {
        change2FABtn.addEventListener('click', async function() {
            // Kiểm tra phương thức xác thực hiện tại
            try {
                const response = await fetch('/accounts/security/get-2fa-method/');
                const data = await response.json();
                
                if (data.method !== 'password') {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Phương thức bạn chọn không phù hợp để đổi mật khẩu'
                    });
                    return;
                }
                
                // Nếu là phương thức mật khẩu, hiển thị modal đổi mật khẩu
                const change2FAPasswordModal = new bootstrap.Modal(document.getElementById('change2FAPasswordModal'));
                change2FAPasswordModal.show();
                
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        });
    }

    // Xử lý form đổi mật khẩu cấp 2
    const change2FAPasswordForm = document.getElementById('change2FAPasswordForm');
    if (change2FAPasswordForm) {
        change2FAPasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current2FAPassword').value;
            const newPassword = document.getElementById('new2FAPassword').value;
            const confirmPassword = document.getElementById('confirm2FAPassword').value;
            
            // Validate mật khẩu mới
            if (newPassword.length < 6) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Mật khẩu cấp 2 phải có ít nhất 6 ký tự'
                });
                return;
            }

            if (!/\d/.test(newPassword)) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Mật khẩu cấp 2 phải chứa ít nhất 1 số'
                });
                return;
            }

            if (newPassword !== confirmPassword) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Mật khẩu xác nhận không khớp'
                });
                return;
            }

            try {
                const formData = new FormData(this);
                const response = await fetch('/accounts/security/change-2fa-password/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('change2FAPasswordModal'));
                    modal.hide();
                    
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: 'Bạn đã đổi mật khẩu cấp 2 thành công'
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: data.message || 'Mật khẩu cấp 2 hiện tại không đúng'
                    });
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        });
    }

    // Xử lý đổi phương thức xác thực
    const change2FAMethodBtn = document.getElementById('change2FAMethodBtn');
    if (change2FAMethodBtn) {
        change2FAMethodBtn.addEventListener('click', async function() {
            try {
                // Hiển thị modal setup2FA
                modals.setup2FA.show();
                
                // Lấy phương thức hiện tại và set giá trị cho select
                const response = await fetch('/accounts/security/get-2fa-method/');
                const data = await response.json();
                if (data.method) {
                    document.getElementById('2fa_method').value = data.method;
                    handle2FAMethodChange(); // Trigger change event để hiển thị form tương ứng
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        });
    }

    // Xử lý cài đặt trường hợp áp dụng
    const edit2FASettingsBtn = document.getElementById('edit2FASettingsBtn');
    if (edit2FASettingsBtn) {
        edit2FASettingsBtn.addEventListener('click', function() {
            modals.edit2FASettings.show();
        });
    }

    // Xử lý xóa mật khẩu cấp 2
    const delete2FABtn = document.getElementById('delete2FABtn');
    if (delete2FABtn) {
        delete2FABtn.addEventListener('click', async function() {
            try {
                // Lấy phương thức xác thực hiện tại
                const response = await fetch('/accounts/security/get-2fa-method/');
                const data = await response.json();
                
                // Hiển thị modal xác thực tương ứng
                switch (data.method) {
                    case 'password':
                        modals.verify2FA.show();
                        break;
                    case 'email':
                        await sendOTP();
                        modals.verifyOTP.show();
                        startCountdown(); // Bắt đầu đếm ngược cho OTP
                        break;
                    case 'google_authenticator':
                        modals.verifyGA.show();
                        break;
                    default:
                        throw new Error('Phương thức xác thực không hợp lệ');
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        });
    }

    // Xử lý form cài đặt
    const edit2FASettingsForm = document.getElementById('edit2FASettingsForm');
    if (edit2FASettingsForm) {
        edit2FASettingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const settings = {
                purchase: document.getElementById('edit_2fa_purchase').checked,
                deposit: document.getElementById('edit_2fa_deposit').checked,
                password: document.getElementById('edit_2fa_password').checked,
                profile: document.getElementById('edit_2fa_profile').checked
            };

            if (!Object.values(settings).some(value => value)) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Vui lòng chọn ít nhất một trường hợp áp dụng xác thực'
                });
                return;
            }

            try {
                const response = await fetch('/accounts/security/update-2fa-settings/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(settings)
                });

                const data = await response.json();
                
                if (data.status === 'success') {
                    modals.edit2FASettings.hide();
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: 'Đã cập nhật cài đặt thành công'
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        });
    }

    // Xử lý OTP verification
    function setupOTPVerification() {
        const otpInputs = document.querySelectorAll('.otp-input');
        const verifyOTPForm = document.getElementById('verifyOTPForm');
        const resendOTPBtn = document.getElementById('resendOTPBtn');
        const backToVerifyBtn = document.getElementById('backToVerifyBtn');
        let countdownInterval;

        // Xử lý input OTP
        otpInputs.forEach((input, index) => {
            input.addEventListener('keyup', (e) => {
                const currentInput = e.target;
                const nextInput = otpInputs[index + 1];
                const prevInput = otpInputs[index - 1];

                // Xóa các ký tự không phải số
                currentInput.value = currentInput.value.replace(/[^0-9]/g, '');

                if (currentInput.value.length > 1) {
                    currentInput.value = currentInput.value[0];
                }

                if (currentInput.value !== '' && nextInput) {
                    nextInput.focus();
                }

                if (e.key === 'Backspace' && prevInput) {
                    prevInput.focus();
                }
            });
        });

        // Xử lý submit form OTP
        if (verifyOTPForm) {
            verifyOTPForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const otp = Array.from(otpInputs).map(input => input.value).join('');
                
                if (otp.length !== 6) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Vui lòng nhập đủ 6 số'
                    });
                    return;
                }

                try {
                    const response = await fetch('/accounts/security/verify-otp/', {
                        method: 'POST',
                        body: JSON.stringify({ otp }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    const data = await response.json();

                    if (data.status === 'success') {
                        // Ẩn modal OTP và hiện modal tiếp theo
                        const verifyOTPModal = bootstrap.Modal.getInstance(document.getElementById('verifyOTPModal'));
                        verifyOTPModal.hide();
                        setup2FAModal.show();
                    } else {
                        // Reset form và hiển thị lỗi
                        otpInputs.forEach(input => input.value = '');
                        otpInputs[0].focus();
                        Swal.fire({
                            icon: 'error',
                            title: 'Lỗi',
                            text: data.message || 'Mã OTP không đúng'
                        });
                    }
                } catch (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                    });
                }
            });
        }

        // Xử lý đếm ngược và gửi lại OTP
        function startCountdown() {
            let timeLeft = 60;
            const timerDisplay = document.getElementById('countdownTimer');
            resendOTPBtn.disabled = true;

            countdownInterval = setInterval(() => {
                timeLeft--;
                timerDisplay.textContent = timeLeft;

                if (timeLeft <= 0) {
                    clearInterval(countdownInterval);
                    resendOTPBtn.disabled = false;
                }
            }, 1000);
        }

        // Xử lý gửi lại OTP
        if (resendOTPBtn) {
            resendOTPBtn.addEventListener('click', async () => {
                if (!resendOTPBtn.disabled) {
                    try {
                        const response = await fetch('/accounts/security/resend-otp/', {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                            }
                        });

                        const data = await response.json();

                        if (data.status === 'success') {
                            startCountdown();
                            Swal.fire({
                                icon: 'success',
                                title: 'Thành công',
                                text: 'Đã gửi lại mã OTP'
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Lỗi',
                                text: data.message || 'Không thể gửi lại mã OTP'
                            });
                        }
                    } catch (error) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Lỗi',
                            text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                        });
                    }
                }
            });
        }

        // Xử lý nút quay lại
        if (backToVerifyBtn) {
            backToVerifyBtn.addEventListener('click', () => {
                const verifyOTPModal = bootstrap.Modal.getInstance(document.getElementById('verifyOTPModal'));
                verifyOTPModal.hide();
                // Hiện lại modal trước đó
                verify2FAModal.show();
            });
        }

        // Bắt đầu đếm ngược khi hiện modal
        startCountdown();
    }

    // Xử lý Google Authenticator
    function setupGoogleAuthenticator() {
        // Lấy QR code và secret key từ server khi chọn phương thức GA
        async function getGASetupData() {
            try {
                const response = await fetch('/accounts/security/setup-ga/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Cập nhật QR code và secret key
                    document.getElementById('gaQrCode').src = data.qr_code;
                    document.getElementById('gaSecretKey').textContent = data.secret_key;
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: data.message || 'Không thể tạo mã QR'
                    });
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                });
            }
        }

        // Xử lý khi chọn phương thức Google Authenticator
        document.getElementById('2fa_method').addEventListener('change', function(e) {
            if (e.target.value === 'google_authenticator') {
                getGASetupData();
            }
        });

        // Xử lý submit form xác thực GA
        const verifyGAForm = document.getElementById('verifyGAForm');
        if (verifyGAForm) {
            verifyGAForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const otpInputs = document.querySelectorAll('.ga-verify-otp');
                const otp = Array.from(otpInputs).map(input => input.value).join('');
                
                if (otp.length !== 6) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Vui lòng nhập đủ 6 số'
                    });
                    return;
                }

                try {
                    const response = await fetch('/accounts/security/verify-ga/', {
                        method: 'POST',
                        body: JSON.stringify({ otp }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                        }
                    });

                    const data = await response.json();

                    if (data.status === 'success') {
                        // Ẩn modal GA và hiện modal tiếp theo hoặc hoàn tất
                        const verifyGAModal = bootstrap.Modal.getInstance(document.getElementById('verifyGAModal'));
                        verifyGAModal.hide();
                        
                        Swal.fire({
                            icon: 'success',
                            title: 'Thành công',
                            text: 'Xác thực thành công'
                        }).then(() => {
                            // Tiếp tục quy trình hoặc reload trang
                            window.location.reload();
                        });
                    } else {
                        // Reset form và hiển thị lỗi
                        otpInputs.forEach(input => input.value = '');
                        otpInputs[0].focus();
                        Swal.fire({
                            icon: 'error',
                            title: 'Lỗi',
                            text: data.message || 'Mã xác thực không đúng'
                        });
                    }
                } catch (error) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Đã có lỗi xảy ra, vui lòng thử lại'
                    });
                }
            });
        }

        // Xử lý nút quay lại
        const backToVerifyGABtn = document.getElementById('backToVerifyGABtn');
        if (backToVerifyGABtn) {
            backToVerifyGABtn.addEventListener('click', () => {
                const verifyGAModal = bootstrap.Modal.getInstance(document.getElementById('verifyGAModal'));
                verifyGAModal.hide();
                // Hiện lại modal trước đó
                const previousModal = bootstrap.Modal.getInstance(document.getElementById('setup2FAModal'));
                if (previousModal) {
                    previousModal.show();
                }
            });
        }

        // Xử lý input OTP cho Google Authenticator
        const gaOtpInputs = document.querySelectorAll('.ga-otp, .ga-verify-otp');
        gaOtpInputs.forEach((input, index) => {
            input.addEventListener('keyup', (e) => {
                const currentInput = e.target;
                const nextInput = gaOtpInputs[index + 1];
                const prevInput = gaOtpInputs[index - 1];

                // Xóa các ký tự không phải số
                currentInput.value = currentInput.value.replace(/[^0-9]/g, '');

                if (currentInput.value.length > 1) {
                    currentInput.value = currentInput.value[0];
                }

                if (currentInput.value !== '' && nextInput) {
                    nextInput.focus();
                }

                if (e.key === 'Backspace' && prevInput) {
                    prevInput.focus();
                }
            });
        });
    }

    // Khởi tạo Google Authenticator
    setupGoogleAuthenticator();

    // Xử lý OTP verification
    setupOTPVerification();
});

// Xử lý sự kiện cho nút Đổi và Xóa mật khẩu cấp 2
document.getElementById('change_password_btn').addEventListener('click', function () {
    alert('Chức năng đổi mật khẩu cấp 2 đang được xử lý.');
});

document.getElementById('delete_password_btn').addEventListener('click', function () {
    alert('Chức năng xóa mật khẩu cấp 2 đang được xử lý.');
});