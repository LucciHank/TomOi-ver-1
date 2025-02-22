document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('depositForm');
    const amountInput = document.getElementById('amount');
    const methodInputs = document.querySelectorAll('input[name="paymentMethod"]');
    
    // Xử lý hiển thị các trường theo phương thức thanh toán
    methodInputs.forEach(input => {
        input.addEventListener('change', function() {
            const method = this.value;
            document.querySelectorAll('.method-fields').forEach(div => {
                div.style.display = 'none';
            });
            document.getElementById(`${method}Fields`).style.display = 'block';
        });
    });

    // Format số tiền khi nhập
    amountInput.addEventListener('input', function() {
        let value = this.value.replace(/\D/g, '');
        if (value) {
            value = parseInt(value).toLocaleString('vi-VN');
            this.value = value;
        }
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const amount = parseInt(amountInput.value.replace(/\D/g, ''));
        const method = document.querySelector('input[name="paymentMethod"]:checked').value;
        
        if (amount < 10000) {
            showError('Số tiền tối thiểu là 10.000đ');
            return;
        }

        try {
            const response = await fetch('/accounts/deposit/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    amount: amount,
                    payment_method: method
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else if (data.bank_info) {
                    showBankingInfo(data.bank_info);
                }
            } else {
                showError(data.message);
            }
        } catch (error) {
            showError('Có lỗi xảy ra, vui lòng thử lại');
        }
    });
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