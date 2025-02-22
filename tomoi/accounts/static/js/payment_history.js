document.addEventListener('DOMContentLoaded', function() {
    // Click handler cho balance boxes
    const balanceBoxes = document.querySelectorAll('.balance-box');
    
    balanceBoxes[0].addEventListener('click', function() {
        window.location.href = '/accounts/deposit/';
    });

    balanceBoxes[1].addEventListener('click', function() {
        window.location.href = '/accounts/tcoin/';
    });

    // Thêm hiệu ứng ripple khi click
    balanceBoxes.forEach(box => {
        box.style.cursor = 'pointer';
        
        box.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size/2}px`;
            ripple.style.top = `${e.clientY - rect.top - size/2}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}); 