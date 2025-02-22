function checkIn() {
    const button = document.querySelector('button[onclick="checkIn()"]');
    button.disabled = true;
    
    fetch('/accounts/tcoin/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const modal = new bootstrap.Modal(document.getElementById('checkinModal'));
            document.getElementById('checkinMessage').textContent = 'Bạn đã điểm danh thành công!';
            modal.show();
            setTimeout(() => {
                modal.hide();
                location.reload();
            }, 2000);
        } else {
            showError(data.message);
            button.disabled = false;
        }
    })
    .catch(error => {
        showError('Có lỗi xảy ra, vui lòng thử lại');
        button.disabled = false;
    });
}

// Countdown timer
function updateCountdown() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    
    const diff = tomorrow - now;
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    
    document.getElementById('nextCheckin').textContent = 
        `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

if (document.getElementById('nextCheckin')) {
    updateCountdown();
    setInterval(updateCountdown, 1000);
} 