// Định nghĩa hàm global
function showVerifyCurrentEmailModal() {
    const verifyCurrentEmailModal = new bootstrap.Modal(document.getElementById('verifyCurrentEmailModal'));
    verifyCurrentEmailModal.show();
}

function showVerifyOTPModal() {
    const verifyOTPModal = new bootstrap.Modal(document.getElementById('verifyOTPModal'));
    verifyOTPModal.show();
}

document.addEventListener('DOMContentLoaded', function() {
    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    
    // Hàm xử lý preview avatar
    window.previewAvatar = function(input) {
        if (input.files && input.files[0]) {
            const maxSize = 5 * 1024 * 1024; // 5MB
            if (input.files[0].size > maxSize) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Kích thước ảnh không được vượt quá 5MB'
                });
                input.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                const previewImg = document.querySelector('.preview-avatar');
                if (previewImg) {
                    previewImg.src = e.target.result;
                }
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Gán sự kiện cho input file
    const avatarInput = document.querySelector('input[name="avatar"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            previewAvatar(this);
        });
    }

    // Xử lý form submit
    const editProfileForm = document.getElementById('editProfileForm');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('/accounts/update-profile/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: data.message,
                        showConfirmButton: false,
                        timer: 1500
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
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Có lỗi xảy ra, vui lòng thử lại'
                });
            });
        });
    }

   // Khởi tạo các modal
const verifyCurrentEmailModal = new bootstrap.Modal(document.getElementById('verifyCurrentEmailModal'));
const verifyOTPModal = new bootstrap.Modal(document.getElementById('verifyOTPModal'));
const emailInput = document.querySelector('input[name="email"]');
let countdownInterval;

// Xử lý nút edit email
document.querySelectorAll('.edit-email-btn').forEach(button => {
    button.addEventListener('click', function() {
        verifyCurrentEmailModal.show();
    });
});

// Xử lý form xác thực email hiện tại
document.getElementById('verifyCurrentEmailForm')?.addEventListener('submit', async function(e) {
    e.preventDefault(); // Ngăn form submit mặc định
    
    const currentEmail = document.getElementById('currentEmailInput').value.trim();
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
            // Hiển thị email đã mask trong modal OTP
            document.getElementById('maskedEmailOTP').textContent = data.masked_email;
            
            // Chuyển sang modal nhập OTP
            verifyCurrentEmailModal.hide();
            verifyOTPModal.show();
            
            // Reset form và bắt đầu đếm ngược
            this.reset();
            startCountdown();
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi!',
                text: data.message || 'Xác thực thất bại!',
                confirmButtonColor: '#e50914'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Lỗi hệ thống!',
            text: 'Vui lòng thử lại sau',
            confirmButtonColor: '#e50914'
        });
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Gửi mã OTP';
    }
});

// Xử lý form xác thực OTP
document.getElementById('verifyOTPForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const otp = document.getElementById('otpInput').value.trim();
    const submitBtn = this.querySelector('button[type="submit"]');

    try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Đang xác thực...';
        
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
            // Hiển thị thông báo thành công
            Swal.fire({
                icon: 'success',
                title: 'Xác thực thành công!',
                text: 'Bạn có thể thay đổi email mới.',
                confirmButtonColor: '#e50914'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Đóng modal OTP
                    verifyOTPModal.hide();
                    
                    // Hiển thị lại modal chỉnh sửa thông tin
                    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
                    editProfileModal.show();
                    
                    // Mở khóa trường email trong modal chỉnh sửa thông tin
                    const emailInput = document.querySelector('#editProfileModal input[name="email"]');
                    emailInput.readOnly = false;
                    emailInput.classList.remove('bg-light');
                    emailInput.value = ''; // Xóa email cũ
                    emailInput.focus();
                }
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi!',
                text: data.message || 'OTP không hợp lệ',
                confirmButtonColor: '#e50914'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Lỗi hệ thống!',
            text: 'Vui lòng thử lại sau',
            confirmButtonColor: '#e50914'
        });
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Xác thực';
    }
});

// Xử lý đếm ngược OTP
function startCountdown() {
    let timeLeft = 60;
    const countdownSpan = document.getElementById('countdown');
    const resendBtn = document.getElementById('resendOTPBtn');
    
    resendBtn.disabled = true;
    clearInterval(countdownInterval);
    
    countdownInterval = setInterval(() => {
        timeLeft--;
        countdownSpan.textContent = `(${timeLeft}s)`;
        
        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            resendBtn.disabled = false;
            countdownSpan.textContent = '';
        }
    }, 1000);
}

// Xử lý gửi lại OTP
document.getElementById('resendOTPBtn')?.addEventListener('click', async function() {
    try {
        this.disabled = true;
        const response = await fetch('/accounts/send-email-change-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `resend=true`
        });

        const data = await response.json();
        if (data.status === 'success') {
            startCountdown();
            Swal.fire({
                icon: 'success',
                title: 'Đã gửi lại OTP!',
                confirmButtonColor: '#e50914'
            });
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

// Reset form khi modal đóng
verifyCurrentEmailModal._element.addEventListener('hidden.bs.modal', () => {
    document.getElementById('verifyCurrentEmailForm').reset();
});

verifyOTPModal._element.addEventListener('hidden.bs.modal', () => {
    document.getElementById('verifyOTPForm').reset();
    clearInterval(countdownInterval);
    document.getElementById('countdown').textContent = '';
});
}); 