document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.getElementById('submitBtn');
    const amountInput = document.getElementById('amount');

    if (submitBtn) {
        submitBtn.addEventListener('click', async function() {
            try {
                submitBtn.disabled = true;
                
                const amount = amountInput.value.replace(/[,.]/g, '');
                const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;

                if (parseInt(amount) < 10000) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: 'Số tiền nạp tối thiểu là 10.000đ'
                    });
                    return;
                }

                if (paymentMethod === 'vnpay') {
                    const response = await fetch('/accounts/deposit/create-payment/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            amount: parseInt(amount),
                            payment_method: 'vnpay'
                        })
                    });

                    const data = await response.json();
                    console.log('Response:', data);

                    if (data.success && data.payment_url) {
                        window.location.href = data.payment_url;
                    } else {
                        throw new Error(data.message || 'Có lỗi xảy ra khi tạo thanh toán');
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Không thể kết nối đến cổng thanh toán'
                });
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // Format số tiền khi nhập
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value) {
                value = parseInt(value).toLocaleString('vi-VN');
                this.value = value;
            }
        });
    }

    // Xử lý khi chọn phương thức thanh toán
    const cardPaymentLabel = document.querySelector('label[for="cardPayment"]');
    if (cardPaymentLabel) {
        cardPaymentLabel.addEventListener('click', function(e) {
            // Ngăn chặn hành vi mặc định của form
            e.preventDefault();
            e.stopPropagation();
            
            // Hiển thị modal nạp thẻ
            const cardModal = new bootstrap.Modal(document.getElementById('cardModal'));
            cardModal.show();
        });
    }

    // Xử lý form nạp thẻ cào
    const cardDepositForm = document.getElementById('cardDepositForm');
    if (cardDepositForm) {
        cardDepositForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validate dữ liệu
            const amount = document.getElementById('cardAmount').value;
            const telco = document.getElementById('cardType').value;
            const serial = document.getElementById('cardSerial').value.trim();
            const pin = document.getElementById('cardPin').value.trim();

            if (!telco || !serial || !pin) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Vui lòng điền đầy đủ thông tin thẻ'
                });
                return;
            }

            try {
                const response = await fetch('/accounts/deposit/card/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        telco: telco,
                        serial: serial,
                        pin: pin,
                        amount: amount
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    // Đóng modal
                    bootstrap.Modal.getInstance(document.getElementById('cardModal')).hide();
                    
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: 'Thẻ đang được xử lý, vui lòng đợi trong giây lát',
                        showConfirmButton: false,
                        timer: 2000
                    });
                    // Reset form
                    cardDepositForm.reset();
                } else {
                    throw new Error(data.message);
                }
            } catch (error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: error.message || 'Có lỗi xảy ra, vui lòng thử lại sau'
                });
            }
        });
    }
});

function showBankingInfo(info) {
    const modal = new bootstrap.Modal(document.getElementById('bankingModal'));
    document.getElementById('accountNumber').textContent = info.account_number;
    document.getElementById('bankName').textContent = info.bank_name;
    document.getElementById('accountName').textContent = info.account_name;
    document.getElementById('transferAmount').textContent = formatMoney(info.amount);
    document.getElementById('transferContent').textContent = info.content;
    
    // Thêm nút copy cho từng trường
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            const text = this.previousElementSibling.textContent;
            navigator.clipboard.writeText(text);
            showSuccess('Đã sao chép');
        });
    });
    
    modal.show();
}

function formatMoney(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

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