// Thêm event listener khi trang load
document.addEventListener('DOMContentLoaded', function() {
    const balanceBtn = document.getElementById('pay-with-balance-btn');
    if (balanceBtn) {
        balanceBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Ngăn chặn hành vi mặc định
            
            const cartTotal = parseFloat(document.querySelector('.total-row .final-amount').textContent.replace(/[^0-9]/g, ''));
            const userBalance = parseFloat(this.dataset.balance);
            
            if (userBalance < cartTotal) {
                Swal.fire({
                    icon: 'error',
                    title: 'Số dư không đủ',
                    text: 'Vui lòng nạp thêm tiền để thanh toán'
                });
                return;
            }
            
            // Nếu đủ số dư thì chuyển trang
            window.location.href = this.getAttribute('onclick').match(/'([^']+)'/)[1];
        });
    }
});

async function processPayment(authType, authValue) {
    try {
        const response = await fetch('/store/pay-with-balance/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cart_total: document.getElementById('cart-total').dataset.total,
                auth_type: authType,
                auth_value: authValue
            })
        });
        
        const data = await response.json();
        if (data.success) {
            window.location.href = `/accounts/success/?title=Thanh toán thành công&message=Đơn hàng #${data.order_id} đã được thanh toán thành công`;
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: data.message
            });
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Lỗi',
            text: 'Có lỗi xảy ra khi xử lý thanh toán'
        });
    }
}

function setupOTPInputs() {
    const inputs = document.querySelectorAll('.otp-input');
    inputs.forEach((input, index) => {
        input.addEventListener('keyup', (e) => {
            if (e.key >= '0' && e.key <= '9') {
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            } else if (e.key === 'Backspace') {
                if (index > 0) {
                    inputs[index - 1].focus();
                }
            }
        });
    });
}

// Thêm hàm getCookie nếu chưa có
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

// Thêm CSS cho OTP inputs
document.head.insertAdjacentHTML('beforeend', `
<style>
.otp-inputs {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
}

.otp-input {
    width: 40px;
    height: 40px;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 18px;
}

.otp-input::-webkit-outer-spin-button,
.otp-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
</style>
`); 