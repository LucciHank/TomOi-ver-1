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
        faMethodSelect.addEventListener('change', async function() {
            const method = this.value;
            const setup2FAForm = document.getElementById('setup2FAForm');
            
            if (!setup2FAForm) {
                console.error('Không tìm thấy form setup 2FA');
                return;
            }
            
            // Ẩn tất cả các section
            document.querySelectorAll('.setup-section').forEach(section => {
                section.classList.add('d-none');
            });
            
            if (method === 'google_authenticator') {
                try {
                    // Gọi API để lấy QR code và secret key
                    const response = await fetch('/accounts/security/setup-ga/');
                    const data = await response.json();
                    
                    if (data.status === 'success' && data.qr_code && data.secret_key) {
                        // Tạo và hiển thị section GA
                        const template = `
                            <div id="gaSection" class="setup-section mt-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="text-center mb-3">
                                            <img id="gaQrCode" src="data:image/png;base64,${data.qr_code}" alt="QR Code" class="img-fluid">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">Secret Key:</label>
                                            <div class="input-group">
                                                <input type="text" id="gaSecretKey" class="form-control" 
                                                       value="${data.secret_key}" readonly 
                                                       style="color: #df2626; font-weight: 500;">
                                                <button class="btn btn-outline-secondary" type="button" onclick="copySecretKey()" 
                                                        title="Sao chép mã bí mật" style="color: #df2626; border-color: #df2626;">
                                                    <i class="fas fa-copy"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label for="gaOtpInput" class="form-label">Nhập mã xác thực:</label>
                                            <input type="text" 
                                                   id="gaOtpInput" 
                                                   class="form-control" 
                                                   maxlength="6" 
                                                   pattern="[0-9]*" 
                                                   inputmode="numeric"
                                                   placeholder="Nhập 6 số từ ứng dụng">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // Xóa section GA cũ nếu có
                        const oldSection = document.getElementById('gaSection');
                        if (oldSection) {
                            oldSection.remove();
                        }
                        
                        // Thêm section mới và hiển thị
                        setup2FAForm.insertAdjacentHTML('beforeend', template);
                        document.getElementById('gaSection').classList.remove('d-none');
                        
                        // Thêm hover effect cho nút copy
                        const copyBtn = document.querySelector('button[onclick="copySecretKey()"]');
                        if (copyBtn) {
                            copyBtn.addEventListener('mouseenter', function() {
                                this.style.backgroundColor = '#df2626';
                                this.style.color = '#fff';
                            });
                            copyBtn.addEventListener('mouseleave', function() {
                                this.style.backgroundColor = '';
                                this.style.color = '#df2626';
                            });
                        }
                        
                        // Lưu secret key vào form
                        let hiddenInput = document.querySelector('input[name="ga_secret_key"]');
                        if (!hiddenInput) {
                            hiddenInput = document.createElement('input');
                            hiddenInput.type = 'hidden';
                            hiddenInput.name = 'ga_secret_key';
                            setup2FAForm.appendChild(hiddenInput);
                        }
                        hiddenInput.value = data.secret_key;
                    } else {
                        throw new Error(data.message || 'Không nhận được dữ liệu QR code');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: error.message || 'Không thể tạo mã QR. Vui lòng thử lại sau.'
                    });
                    
                    // Reset select về giá trị mặc định
                    faMethodSelect.value = '';
                }
            }
        });
    }

    // Xử lý form setup 2FA
    const setup2FAForm = document.getElementById('setup2FAForm');
    if (setup2FAForm) {
        setup2FAForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const method = document.getElementById('fa_method').value;
            
            try {
                if (method === 'google_authenticator') {
                    const gaOtp = document.getElementById('gaOtpInput').value.trim();
                    const secretKeyInput = document.querySelector('input[name="ga_secret_key"]');
                    
                    if (!secretKeyInput || !secretKeyInput.value) {
                        throw new Error('Không tìm thấy secret key');
                    }
                    
                    if (!gaOtp) {
                        throw new Error('Vui lòng nhập mã xác thực');
                    }
                    
                    if (!/^\d{6}$/.test(gaOtp)) {
                        throw new Error('Mã xác thực phải là 6 số');
                    }
                    
                    console.log('Sending setup request:', {
                        method: 'google_authenticator',
                        otp: gaOtp,
                        secret_key: secretKeyInput.value
                    });
                    
                    // Verify mã OTP và lưu secret key
                    const response = await fetch('/accounts/security/setup-2fa/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            method: 'google_authenticator',
                            otp: gaOtp,
                            secret_key: secretKeyInput.value
                        })
                    });

                    const data = await response.json();
                    if (data.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Thành công',
                            text: 'Đã thiết lập xác thực 2 lớp',
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
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Có lỗi xảy ra'
                });
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
            'password': 'Mật khẩu cấp 2',
            'email': 'OTP qua email',
            'google_authenticator': 'Google Authenticator'
        };

        const template = `
            <div class="alert alert-info">
                <i class="fas fa-shield-alt me-2"></i>
                Bạn đang sử dụng <strong>${methodNames[method]}</strong> để xác thực 2 lớp.
            </div>
            <div class="mt-3">
                ${method === 'password' ? `
                    <button type="button" class="btn btn-primary me-2" id="change2FABtn">
                        <i class="fas fa-key me-2"></i>Đổi mật khẩu cấp 2
                    </button>
                ` : ''}
                <button type="button" class="btn btn-outline-danger" id="delete2FABtn">
                    <i class="fas fa-trash-alt me-2"></i>Xóa xác thực 2 lớp
                </button>
            </div>
        `;

        container.innerHTML = template;
    }

    // Thêm hàm kiểm tra và cập nhật UI khi tải trang
    async function check2FAStatus() {
        try {
            const response = await fetch('/accounts/security/check-2fa-status/');
            const data = await response.json();
            
            if (data.has_2fa && data.method) {
                updateUI2FAStatus(data.method);
            }
        } catch (error) {
            console.error('Error checking 2FA status:', error);
        }
    }

    // Gọi hàm kiểm tra khi tải trang
    document.addEventListener('DOMContentLoaded', check2FAStatus);

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
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            try {
                const currentPassword = document.getElementById('current_password_change').value;
                const newPassword = document.getElementById('new_password_change').value;
                const confirmPassword = document.getElementById('confirm_password_change').value;

                if (newPassword !== confirmPassword) {
                    throw new Error('Mật khẩu mới và xác nhận mật khẩu không khớp');
                }

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
                        text: 'Đã đổi mật khẩu thành công',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        window.location.reload();
                    });
            } else {
                    throw new Error(data.message || 'Có lỗi xảy ra');
            }
        } catch (error) {
            Swal.fire({
                icon: 'error',
                    title: 'Lỗi',
                    text: error.message
                });
            }
        });
    }

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

    // Xử lý nút xóa mật khẩu cấp 2
    const deleteBtn = document.getElementById('delete2FABtn');
    if (deleteBtn) {
        console.log('Found delete2FABtn'); // Debug log
        
        deleteBtn.addEventListener('click', async function() {
            try {
                // Hiện dialog xác nhận trước
                const confirmResult = await Swal.fire({
                    title: 'Xác nhận xóa',
                    text: 'Bạn có chắc muốn xóa xác thực 2 lớp không?',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Có',
                    cancelButtonText: 'Hủy',
                    confirmButtonColor: '#dc3545'
                });

                if (confirmResult.isConfirmed) {
                    // Kiểm tra phương thức 2FA hiện tại
                    const statusResponse = await fetch('/accounts/security/check-2fa-status/');
                    const statusData = await statusResponse.json();
                    console.log('2FA Status:', statusData); // Debug log

                    if (!statusData.has_2fa) {
                        throw new Error('Bạn chưa thiết lập xác thực 2 lớp');
                    }

                    // Nếu đang dùng Google Authenticator
                    if (statusData.method === 'google_authenticator') {
                        // Hiển thị dialog nhập OTP
                        const { value: otp } = await Swal.fire({
                            title: 'Xác nhận mã Google Authenticator',
                            html: `
                                <div class="mb-3">
                                    <label for="otpInput" class="form-label">Nhập mã từ ứng dụng Google Authenticator</label>
                                    <input type="text" 
                                           id="otpInput" 
                                           class="form-control text-center" 
                                           maxlength="6" 
                                           pattern="[0-9]*" 
                                           inputmode="numeric"
                                           autocomplete="off"
                                           placeholder="Nhập 6 số">
                                </div>
                            `,
                            focusConfirm: false,
                            showCancelButton: true,
                            confirmButtonText: 'Xác nhận',
                            cancelButtonText: 'Hủy',
                            preConfirm: () => {
                                const otpInput = document.getElementById('otpInput');
                                const otpValue = otpInput.value.trim();
                                
                                if (!otpValue) {
                                    Swal.showValidationMessage('Vui lòng nhập mã xác thực!');
                                    return false;
                                }
                                
                                if (!/^\d{6}$/.test(otpValue)) {
                                    Swal.showValidationMessage('Mã xác thực phải là 6 số!');
                                    return false;
                                }
                                
                                return otpValue;
                            }
                        });

                        if (otp) {
                            console.log('Sending OTP:', otp); // Debug log

                            // Verify mã GA
                            const verifyResponse = await fetch('/accounts/security/verify-ga/', {
            method: 'POST',
            headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': getCookie('csrftoken')
                                },
                                body: JSON.stringify({ otp: otp })
                            });

                            const verifyData = await verifyResponse.json();
                            console.log('Verify Response:', verifyData); // Debug log

                            if (verifyResponse.ok && verifyData.status === 'success') {
                                // Nếu verify thành công, tiến hành xóa 2FA
                                const deleteResponse = await fetch('/accounts/security/delete-2fa/', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': getCookie('csrftoken')
                                    }
                                });

                                const deleteData = await deleteResponse.json();
                                if (deleteResponse.ok && deleteData.status === 'success') {
                                    await Swal.fire({
                                        icon: 'success',
                                        title: 'Thành công',
                                        text: 'Đã xóa xác thực 2 lớp',
                                        showConfirmButton: false,
                                        timer: 1500
                                    });
                                    window.location.reload();
                                } else {
                                    throw new Error(deleteData.message || 'Không thể xóa xác thực 2 lớp');
                                }
                            } else {
                                throw new Error(verifyData.message || 'Mã xác thực không chính xác');
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Không thể xóa xác thực 2 lớp'
                });
            }
        });
    }

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

// Xử lý khi thay đổi phương thức 2FA
document.getElementById('fa_method')?.addEventListener('change', async function() {
    const method = this.value;
    const submitBtn = document.getElementById('setup2FASubmitBtn');
    
    // Ẩn tất cả các trường
    document.querySelectorAll('.fa-fields').forEach(field => {
        field.classList.add('d-none');
    });
    
    // Hiển thị trường tương ứng
    if (method) {
        const fields = document.getElementById(`fa_${method}_fields`);
        if (fields) {
            fields.classList.remove('d-none');
        }
        
        // Xử lý đặc biệt cho Google Authenticator
        if (method === 'google_authenticator') {
            try {
                // Gọi API để lấy QR code và secret key
                const response = await fetch('/accounts/security/setup-ga/');
                const data = await response.json();
                
                if (data.status === 'success') {
                    // Lưu secret key vào session storage để dùng sau
                    sessionStorage.setItem('ga_secret_key', data.secret_key);
                    
                    // Hiển thị QR code và secret key
                    const qrContainer = document.getElementById('gaQrCode');
                    const secretKeyContainer = document.getElementById('gaSecretKey');
                    
                    if (qrContainer) {
                        qrContainer.innerHTML = `<img src="data:image/png;base64,${data.qr_code}" class="img-fluid">`;
                    }
                    if (secretKeyContainer) {
                        secretKeyContainer.textContent = data.secret_key;
                    }
                    
                    // Hiển thị form nhập mã xác thực
                    const verifyForm = document.getElementById('gaVerifyForm');
                    if (verifyForm) {
                        verifyForm.classList.remove('d-none');
                    }
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Không thể thiết lập Google Authenticator'
                });
            }
        }
        
        // Thay đổi text nút submit
        if (submitBtn) {
            submitBtn.innerHTML = method === 'google_authenticator' ? 
                '<i class="fas fa-qrcode me-2"></i>Xác nhận' : 
                '<i class="fas fa-save me-2"></i>Lưu thay đổi';
        }
    }
});

// Xử lý submit form
document.getElementById('setup2FAForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const method = document.getElementById('fa_method').value;
    if (method === 'google_authenticator') {
        const code = document.getElementById('gaCode').value;
        
        if (!code || code.length !== 6) {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: 'Vui lòng nhập đủ 6 số'
            });
            return;
        }
        
        try {
            // Lấy secret key từ session storage
            const secretKey = sessionStorage.getItem('ga_secret_key');
            if (!secretKey) {
                throw new Error('Không tìm thấy secret key. Vui lòng thử lại.');
            }
            
            const response = await fetch('/accounts/security/verify-ga/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    code,
                    secret_key: secretKey
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                // Xóa secret key khỏi session storage
                sessionStorage.removeItem('ga_secret_key');
                
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công',
                    text: 'Đã thiết lập Google Authenticator thành công',
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
                text: error.message || 'Mã không chính xác'
            });
        }
    }
});

// Thêm các hàm xử lý OTP input
function setupOTPInputs() {
    const inputs = document.querySelectorAll('.otp-input');
    inputs.forEach((input, index) => {
        // Tự động focus vào ô đầu tiên
        if (index === 0) input.focus();

        // Xử lý khi nhập số
        input.addEventListener('input', function(e) {
            const value = this.value;
            
            // Chỉ cho phép nhập số
            if (!/^\d*$/.test(value)) {
                this.value = '';
                return;
            }

            if (value.length === 1 && index < inputs.length - 1) {
                // Tự động chuyển focus sang ô tiếp theo
                inputs[index + 1].focus();
            }
        });

        // Xử lý khi nhấn phím
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && !this.value && index > 0) {
                // Quay lại ô trước đó khi xóa
                inputs[index - 1].focus();
            }
        });

        // Xử lý khi paste
        input.addEventListener('paste', function(e) {
        e.preventDefault();
            const pastedData = e.clipboardData.getData('text').trim();
            if (/^\d{6}$/.test(pastedData)) {
                // Nếu paste đúng 6 số, tự động điền vào các ô
                inputs.forEach((input, i) => {
                    input.value = pastedData[i] || '';
                });
                inputs[inputs.length - 1].focus();
            }
        });
    });
}

// Hàm lấy giá trị OTP
function getOTPValue() {
    return Array.from(document.querySelectorAll('.otp-input'))
        .map(input => input.value)
        .join('');
}

// Hàm hiển thị dialog nhập OTP/GA code
function showOTPVerificationDialog(loginId, isLogout = false, method = 'email') {
    let title = isLogout ? 'Xác nhận xóa thiết bị' : 'Xác thực thiết bị';
    let inputLabel = method === 'google_authenticator' ? 
        'Nhập mã từ ứng dụng Google Authenticator' : 
        'Vui lòng nhập mã OTP đã được gửi đến email của bạn';

    return Swal.fire({
        title: title,
        html: `
            <p class="mb-3">${inputLabel}</p>
            <div class="otp-input-container d-flex justify-content-center gap-2 mb-3">
                <input type="text" class="otp-input form-control text-center" maxlength="1" pattern="[0-9]" inputmode="numeric">
                <input type="text" class="otp-input form-control text-center" maxlength="1" pattern="[0-9]" inputmode="numeric">
                <input type="text" class="otp-input form-control text-center" maxlength="1" pattern="[0-9]" inputmode="numeric">
                <input type="text" class="otp-input form-control text-center" maxlength="1" pattern="[0-9]" inputmode="numeric">
                <input type="text" class="otp-input form-control text-center" maxlength="1" pattern="[0-9]" inputmode="numeric">
                <input type="text" class="otp-input form-control text-center" maxlength="1" pattern="[0-9]" inputmode="numeric">
            </div>
            ${method === 'email' ? '<p class="text-muted small">Mã có hiệu lực trong 5 phút</p>' : ''}
        `,
        showCancelButton: true,
        confirmButtonText: 'Xác nhận',
        cancelButtonText: 'Hủy',
        didOpen: () => {
            setupOTPInputs();
        },
        preConfirm: () => {
            const inputs = Swal.getPopup().querySelectorAll('.otp-input');
            const otp = Array.from(inputs)
                .map(input => input.value)
                .join('');
                
            if (otp.length !== 6) {
                Swal.showValidationMessage('Vui lòng nhập đủ 6 số');
                return false;
            }
            return otp;
        }
    });
}

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

// Xử lý nút xác nhận thiết bị và không phải tôi
document.querySelectorAll('.confirm-device-btn, .logout-device-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const loginId = this.dataset.loginId;
        const isLogout = this.classList.contains('logout-device-btn');
        const row = this.closest('tr');
        
        try {
            // Kiểm tra xem người dùng đã có 2FA chưa
            const response = await fetch('/accounts/security/check-2fa-status/');
            const data = await response.json();
            
            if (!data.has_2fa) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Chưa có mật khẩu cấp 2',
                    text: 'Vui lòng thiết lập mật khẩu cấp 2 trước khi thực hiện thao tác này',
                    showCancelButton: true,
                    confirmButtonText: 'Thiết lập ngay',
                    cancelButtonText: 'Để sau'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Hiển thị modal tạo mật khẩu cấp 2
                        showSetup2FAModal();
                    }
                });
                return;
            }

            // Nếu đã có 2FA, kiểm tra phương thức
            if (data.method === 'password') {
                // Hiện modal nhập mật khẩu cấp 2
                const { value: password } = await Swal.fire({
                    title: 'Xác nhận mật khẩu cấp 2',
                    input: 'password',
                    inputLabel: 'Vui lòng nhập mật khẩu cấp 2',
                    inputPlaceholder: 'Nhập mật khẩu cấp 2',
                    showCancelButton: true,
                    confirmButtonText: 'Xác nhận',
                    cancelButtonText: 'Hủy',
                    inputValidator: (value) => {
                        if (!value) {
                            return 'Vui lòng nhập mật khẩu cấp 2!';
                        }
                    }
                });

                if (password) {
                    // Verify mật khẩu cấp 2
                    const verifyResponse = await fetch('/accounts/security/verify-2fa-password/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ password })
                    });

                    const verifyData = await verifyResponse.json();
                    if (!verifyData.status === 'success') {
                        throw new Error('Mật khẩu cấp 2 không chính xác');
                    }
                } else {
                    return;
                }
            } else {
                // Phương thức email hoặc google authenticator
                if (data.method === 'email') {
                    // Hiển thị loading khi gửi OTP
                    Swal.fire({
                        title: 'Đang gửi mã OTP',
                        text: 'Vui lòng đợi trong giây lát...',
                        allowOutsideClick: false,
                        showConfirmButton: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });

                    // Gửi OTP qua email
                    const otpResponse = await fetch('/accounts/security/send-otp-email/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const otpData = await otpResponse.json();
                    if (otpData.status !== 'success') {
                        throw new Error(otpData.message);
                    }
                }

                // Hiển thị modal nhập OTP/GA code và đợi kết quả
                const result = await showOTPVerificationDialog(loginId, isLogout, data.method);
                
                    if (result.isConfirmed) {
                    const otp = result.value;
                    // Verify OTP
                    const verifyResponse = await fetch(data.method === 'google_authenticator' ? 
                        '/accounts/security/verify-ga/' : 
                        '/accounts/security/verify-otp/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ 
                            otp,
                            login_id: loginId,
                            action: isLogout ? 'logout' : 'confirm'
                        })
                    });

                    const verifyData = await verifyResponse.json();
                    if (verifyData.status === 'success') {
                        // Cập nhật UI
                        if (isLogout) {
                            row.remove();
                        } else {
                            const statusCell = row.querySelector('td:nth-last-child(2)');
                            const actionCell = row.querySelector('td:last-child');
                            
                            if (statusCell) {
                                statusCell.innerHTML = '<span class="badge bg-success">Đã xác nhận</span>';
                            }
                            if (actionCell) {
                                actionCell.innerHTML = '';
                            }
                        }

                        // Hiển thị thông báo thành công
                        await Swal.fire({
                            icon: 'success',
                            title: 'Thành công',
                            text: isLogout ? 'Đã xóa thiết bị' : 'Đã xác nhận thiết bị',
                            showConfirmButton: false,
                            timer: 1500
                });
            } else {
                        throw new Error(verifyData.message || 'Mã xác thực không chính xác');
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: error.message || 'Không thể xử lý yêu cầu'
            });
        }
    });
});

// Hàm hiển thị modal tạo mật khẩu cấp 2
function showSetup2FAModal() {
    const modalHtml = `
        <div class="modal fade" id="setup2FAModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Tạo mật khẩu cấp 2</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="password2FAForm">
                            <div class="mb-3">
                                <label for="fa_password" class="form-label">Mật khẩu cấp 2</label>
                                <input type="password" class="form-control" id="fa_password" required>
                            </div>
                            <div class="mb-3">
                                <label for="fa_password_confirm" class="form-label">Xác nhận mật khẩu</label>
                                <input type="password" class="form-control" id="fa_password_confirm" required>
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                                <button type="submit" class="btn btn-primary">Xác nhận</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Thêm modal vào body nếu chưa có
    if (!document.getElementById('setup2FAModal')) {
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    // Hiển thị modal
    const modal = new bootstrap.Modal(document.getElementById('setup2FAModal'));
    modal.show();
}

// Xử lý submit form tạo mật khẩu cấp 2
document.addEventListener('submit', async function(e) {
    if (e.target.id === 'password2FAForm') {
        e.preventDefault();
        
        const password = document.getElementById('fa_password').value;
        const confirmPassword = document.getElementById('fa_password_confirm').value;

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
                bootstrap.Modal.getInstance(document.getElementById('setup2FAModal')).hide();
                
                // Hiển thị thông báo thành công
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công',
                    text: 'Đã thiết lập mật khẩu cấp 2',
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
                text: error.message || 'Không thể thiết lập mật khẩu cấp 2'
            });
        }
    }
});

// Sửa lại CSS cho các button trong bảng thiết bị
const style = document.createElement('style');
style.textContent = `
    .confirm-device-btn, .logout-device-btn {
        font-size: 0.8rem !important;
        padding: 0.25rem 0.5rem !important;
    }
`;
document.head.appendChild(style);



