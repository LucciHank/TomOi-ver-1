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
        change2FAPassword: initializeModal('change2FAPasswordModal'),
        verifyCurrentEmail: initializeModal('verifyCurrentEmailModal')
    };

    // Kiểm tra toggle password
    const initPasswordToggles = () => {
        document.querySelectorAll('.toggle-password').forEach(button => {
            const icon = button.querySelector('i');
            button.addEventListener('click', function() {
                const input = this.previousElementSibling;
                if (!input) return;
                
                const type = input.type === 'password' ? 'text' : 'password';
                input.type = type;
                
                // Thay đổi icon
                if (type === 'text') {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
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

    // Xử lý sự kiện cho nút Đổi và Xóa mật khẩu cấp 2
    const changePasswordBtn = document.getElementById('change_password_btn');
    const deletePasswordBtn = document.getElementById('delete_password_btn');

    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', function () {
            alert('Chức năng đổi mật khẩu cấp 2 đang được xử lý.');
        });
    }

    if (deletePasswordBtn) {
        deletePasswordBtn.addEventListener('click', function () {
            alert('Chức năng xóa mật khẩu cấp 2 đang được xử lý.');
        });
    }

    // Xử lý thay đổi phương thức xác thực
    window.handle2FAMethodChange = function() {
        const method = document.getElementById('fa_method')?.value;
        console.log('Selected method:', method); // Debug log

        // Ẩn tất cả các trường
        const fields = document.querySelectorAll('[id$="_fields"]'); // Tìm tất cả element có id kết thúc bằng "_fields"
        fields.forEach(field => {
            field.classList.add('d-none');
        });

        // Hiển thị trường được chọn và xử lý logic tương ứng
        if (method) {
            const selectedField = document.getElementById(`fa_${method}_fields`);
            if (selectedField) {
                selectedField.classList.remove('d-none');
                console.log('Showing field:', selectedField.id); // Debug log

                switch(method) {
                    case 'password':
                        initPasswordValidation();
                        break;
                    case 'email':
                        handleEmailOTP();
                        break;
                    case 'google':
                        handleGoogleAuth();
                        break;
                }
            } else {
                console.log('Field not found:', `fa_${method}_fields`); // Debug log
            }
        }
    };

    // Xử lý validation mật khẩu
    function initPasswordValidation() {
        const password = document.getElementById('setup_2fa_password');
        const confirm = document.getElementById('setup_2fa_password_confirm');
        const saveBtn = document.querySelector('#setup2FAForm button[type="submit"]');

        if (!password || !confirm || !saveBtn) {
            console.log('Missing elements:', {password, confirm, saveBtn}); // Debug log
            return;
        }

        const validate = () => {
            const isValid = password.value.length >= 6 &&
                          /\d/.test(password.value) &&
                          password.value === confirm.value;
            
            saveBtn.disabled = !isValid;
            console.log('Password validation:', isValid); // Debug log
        };

        password.addEventListener('input', validate);
        confirm.addEventListener('input', validate);
        validate(); // Kích hoạt validation ngay lập tức
    }

    // Xử lý OTP Email
    function handleEmailOTP() {
        sendOTPEmail();
        startCountdown();
    }

    // Gửi OTP qua email
    async function sendOTPEmail() {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }

            const response = await fetch('/accounts/security/send-otp-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({}) // Thêm body rỗng để tránh lỗi
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công',
                    text: data.message
                });
                startCountdown();
                return true;
            } else {
                throw new Error(data.message || 'Không thể gửi mã OTP');
            }
        } catch (error) {
            console.error('Lỗi gửi OTP:', error);
            Swal.fire({
                icon: 'error',
                title: 'Lỗi!',
                text: error.message || 'Không thể gửi mã OTP'
            });
            return false;
        }
    }

    // Xử lý Google Authenticator
    function handleGoogleAuth() {
        setupGoogleAuthenticator();
    }

    // Thiết lập Google Authenticator
    async function setupGoogleAuthenticator() {
        try {
            const response = await fetch('/accounts/security/setup-ga/');
            const data = await response.json();
            
            if (data.status === 'success') {
                const qrCode = document.getElementById('gaQrCode');
                const secretKey = document.getElementById('gaSecretKey');
                
                if (qrCode) qrCode.src = data.qr_code;
                if (secretKey) secretKey.textContent = data.secret;

                // Xử lý input OTP
                const otpInput = document.getElementById('gaOtpInput');
                if (otpInput) {
                    otpInput.value = ''; // Reset input
                    otpInput.addEventListener('input', function() {
                        if (this.value.length === 6) {
                            verifyGoogleAuthenticator(this.value);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Lỗi Google Authenticator:', error);
            Swal.fire('Lỗi!', 'Không thể thiết lập Google Authenticator', 'error');
        }
    }

    let countdownInterval;
    const COUNTDOWN_TIME = 60; // Thời gian đếm ngược (giây)

    function startCountdown() {
        let timeLeft = COUNTDOWN_TIME;
        const resendButton = document.getElementById('resendOTPBtn');
        const countdownSpan = document.getElementById('countdown');
        
        // Disable nút ngay lập tức
        resendButton.disabled = true;
        
        // Cập nhật UI lần đầu
        updateCountdownUI(timeLeft, resendButton, countdownSpan);
        
        // Clear interval cũ nếu có
        if (countdownInterval) {
            clearInterval(countdownInterval);
        }
        
        // Bắt đầu interval mới
        const startTime = Date.now();
        countdownInterval = setInterval(() => {
            const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            timeLeft = COUNTDOWN_TIME - elapsedTime;
            
            if (timeLeft <= 0) {
                clearInterval(countdownInterval);
                resendButton.disabled = false;
                countdownSpan.textContent = '';
                return;
            }
            
            updateCountdownUI(timeLeft, resendButton, countdownSpan);
        }, 1000);
    }

    function updateCountdownUI(timeLeft, resendButton, countdownSpan) {
        countdownSpan.textContent = `(${timeLeft}s)`;
    }

    // Event listener cho nút gửi lại OTP
    document.getElementById('resendOTPBtn')?.addEventListener('click', function(e) {
        e.preventDefault();
        if (this.disabled) return;
        
        // Gọi API gửi lại OTP
        fetch('/accounts/send-otp-email/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                startCountdown();
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Khởi động đếm ngược khi modal mở
    document.getElementById('emailOTPModal')?.addEventListener('shown.bs.modal', function () {
        startCountdown();
    });

    // Dọn dẹp interval khi modal đóng
    document.getElementById('emailOTPModal')?.addEventListener('hidden.bs.modal', function () {
        if (countdownInterval) {
            clearInterval(countdownInterval);
        }
    });

    // Xử lý form setup 2FA
    const init2FASetupForm = () => {
        const form = document.getElementById('setup2FAForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const method = document.getElementById('fa_method').value;
                const formData = new FormData(form);
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

                if (!csrfToken) throw new Error('Missing CSRF token');

                // Nếu là phương thức email, thêm OTP vào formData
                if (method === 'email') {
                    const otpInput = form.querySelector('input[name="otp"]');
                    if (!otpInput?.value) {
                        Swal.fire('Lỗi!', 'Vui lòng nhập mã OTP', 'error');
                        return;
                    }
                }
                
                const response = await fetch('/accounts/security/setup-2fa/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken.value,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(Object.fromEntries(formData))
                });

                if (!response.ok) {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const data = await response.json();
                        throw new Error(data.message || `HTTP error! status: ${response.status}`);
                    } else {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                }

                const data = await response.json();
                if (data.status === 'success') {
                    // Đóng modal trước
                    const modal = bootstrap.Modal.getInstance(document.getElementById('setup2FAModal'));
                    if (modal) {
                        modal.hide();
                        // Xóa backdrop
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) backdrop.remove();
                        document.body.classList.remove('modal-open');
                    }

                    // Sau đó hiển thị thông báo và cập nhật UI
                    await Swal.fire({
                        icon: 'success',
                        title: 'Thành công!',
                        text: data.message
                    });

                    // Cập nhật UI
                    updateUI2FAStatus(method);
                } else {
                    throw new Error(data.message || 'Có lỗi xảy ra');
                }
            } catch (error) {
                console.error('Submission error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi!',
                    text: error.message || 'Có lỗi xảy ra khi thiết lập'
                });
            }
        });
    };

    // Hàm cập nhật UI sau khi setup 2FA
    function updateUI2FAStatus(method) {
        // Ẩn phần setup
        const setupSection = document.querySelector('.no-2fa-message');
        const setupButton = document.getElementById('setup2FABtn');
        if (setupSection) setupSection.style.display = 'none';
        if (setupButton) setupButton.style.display = 'none';

        // Hiển thị phần quản lý 2FA
        const template = `
            <div class="2fa-info mb-4">
                <p class="mb-3">Bạn đã thiết lập mật khẩu cấp 2 với phương thức: 
                    <strong>${getMethodName(method)}</strong>
                </p>
                
                <div class="d-flex gap-2">
                    <button type="button" class="btn btn-outline-danger" id="change2FAMethodBtn">
                        <i class="fas fa-exchange-alt me-2"></i>Đổi phương thức
                    </button>
                    <button type="button" class="btn btn-outline-danger" id="delete2FABtn">
                        <i class="fas fa-trash-alt me-2"></i>Xóa mật khẩu cấp 2
                    </button>
                </div>
            </div>
        `;

        // Chèn template vào DOM
        const container = document.querySelector('.section');
        if (container) {
            container.innerHTML = template;
            // Khởi tạo lại các event listeners
            initModalTriggers();
        }
    }

    // Hàm helper để chuyển đổi tên phương thức
    function getMethodName(method) {
        const methods = {
            'password': 'Tự tạo mật khẩu',
            'email': 'Nhận mã OTP qua email',
            'google': 'Google Authenticator'
        };
        return methods[method] || method;
    }

    // Thêm hàm verify Google Authenticator
    async function verifyGoogleAuthenticator(otp) {
        try {
            const response = await fetch('/accounts/security/verify-ga/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ otp })
            });

            const data = await response.json();
            if (data.status === 'success') {
                updateUI2FAStatus('google');
                const modal = bootstrap.Modal.getInstance(document.getElementById('setup2FAModal'));
                if (modal) modal.hide();
            } else {
                throw new Error(data.message || 'Mã OTP không chính xác');
            }
        } catch (error) {
            Swal.fire('Lỗi!', error.message, 'error');
        }
    }

    // Xử lý nút edit email
    document.querySelector('.edit-email-btn')?.addEventListener('click', function() {
        // Hiển thị modal xác thực email hiện tại
        modals.verifyCurrentEmail?.show();
    });

    // Xử lý form xác thực email hiện tại
    document.getElementById('verifyCurrentEmailForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const currentEmail = document.getElementById('currentEmailInput').value;
        const submitBtn = this.querySelector('button[type="submit"]');
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang gửi...';
            
            const response = await fetch('/accounts/send-email-change-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `current_email=${encodeURIComponent(currentEmail)}`
            });

            const data = await response.json();
            if (data.status === 'success') {
                // Hiển thị email đã được mask trong modal OTP
                document.getElementById('maskedEmailOTP').textContent = data.masked_email;
                
                // Chuyển sang modal nhập OTP
                modals.verifyCurrentEmail?.hide();
                modals.verifyOTP?.show();
                
                // Reset form
                this.reset();
                
                // Bắt đầu đếm ngược
                startCountdown();
            } else {
                Swal.fire('Lỗi!', data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire('Lỗi!', 'Có lỗi xảy ra khi gửi OTP', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Gửi mã OTP';
        }
    });

    // Xử lý form xác thực OTP
    document.getElementById('verifyOTPForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        const otp = document.getElementById('otpInput').value;

        try {
            const response = await fetch('/accounts/verify-email-change-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `otp=${encodeURIComponent(otp)}`
            });

            const data = await response.json();
            if (data.status === 'success') {
                modals.verifyOTP?.hide();
                
                // Cho phép người dùng nhập email mới
                Swal.fire({
                    title: 'Nhập email mới',
                    input: 'email',
                    inputLabel: 'Email mới',
                    inputPlaceholder: 'Nhập địa chỉ email mới',
                    showCancelButton: true,
                    confirmButtonText: 'Xác nhận',
                    cancelButtonText: 'Hủy',
                    inputValidator: (value) => {
                        if (!value) {
                            return 'Vui lòng nhập email!';
                        }
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        updateEmail(result.value);
                    }
                });
            } else {
                Swal.fire('Lỗi!', data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire('Lỗi!', 'Có lỗi xảy ra khi xác thực OTP', 'error');
        }
    });

    // Hàm cập nhật email mới
    async function updateEmail(newEmail) {
        try {
            const response = await fetch('/accounts/update-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: `new_email=${encodeURIComponent(newEmail)}`
            });

            const data = await response.json();
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công!',
                    text: 'Email đã được cập nhật thành công',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    window.location.reload();
                });
            } else {
                Swal.fire('Lỗi!', data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire('Lỗi!', 'Có lỗi xảy ra khi cập nhật email', 'error');
        }
    }

    // Hiển thị email đã được mask khi mở modal xác thực email
    document.getElementById('verifyCurrentEmailModal')?.addEventListener('show.bs.modal', function () {
        const userEmail = document.querySelector('[name="email"]')?.value;
        if (userEmail) {
            document.getElementById('maskedCurrentEmail').textContent = maskEmail(userEmail);
        }
    });

    // Hàm mask email ở client side (tương tự như Python)
    function maskEmail(email) {
        if (!email || !email.includes('@')) return email;
        
        const [localPart, domain] = email.split('@');
        if (localPart.length <= 2) return email;
        
        return `${localPart[0]}${'*'.repeat(localPart.length - 2)}${localPart.slice(-1)}@${domain}`;
    }

    // Khởi động tất cả chức năng
    const initializeAll = () => {
        try {
            initPasswordToggles();
            initModalTriggers();
            init2FASetupForm();
            console.log('All functions initialized');
        } catch (error) {
            console.error('Error initializing functions:', error);
        }
    };

    initializeAll();
});



