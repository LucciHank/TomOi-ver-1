document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabs = document.querySelectorAll('.product-tab-item');
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Variant selection
    const variantOptions = document.querySelectorAll('.variant-option');
    variantOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove active class from all variants
            variantOptions.forEach(opt => opt.classList.remove('active'));
            // Add active class to clicked variant
            this.classList.add('active');
            
            const variantId = this.dataset.variantId;
            updateDurationOptions(variantId);
            updatePrice();
        });
    });

    // Duration selection
    const durationOptions = document.querySelectorAll('.duration-option');
    durationOptions.forEach(option => {
        option.addEventListener('click', function() {
            if (!this.classList.contains('hidden')) {
                durationOptions.forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
                updatePrice();
            }
        });
    });

    // Cross-sale checkboxes
    const crossSaleCheckboxes = document.querySelectorAll('.cross-sale-checkbox');
    crossSaleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateTotalPrice);
    });

    // Initial setup
    const firstVariant = document.querySelector('.variant-option');
    if (firstVariant) {
        firstVariant.click();
    }

    // Xử lý nút yêu thích
    const wishlistBtn = document.querySelector('.wishlist-btn');
    if (wishlistBtn) {
        wishlistBtn.addEventListener('click', async function() {
            const productId = this.getAttribute('data-product-id');
            
            try {
                const response = await fetch('/toggle-wishlist/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        product_id: productId
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'added') {
                    // Thay đổi icon thành trái tim đầy
                    wishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
                    wishlistBtn.classList.add('active');
                } else if (data.status === 'removed') {
                    // Thay đổi icon thành trái tim rỗng
                    wishlistBtn.innerHTML = '<i class="far fa-heart"></i>';
                    wishlistBtn.classList.remove('active');
                }
                
                // Hiển thị thông báo
                Swal.fire({
                    icon: 'success',
                    text: data.message,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    text: 'Có lỗi xảy ra, vui lòng thử lại sau',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            }
        });
    }
    
    // Helper function để lấy cookie
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
});

function selectVariant(element) {
    // Remove active class from all variants
    document.querySelectorAll('.variant-option').forEach(el => {
        el.classList.remove('active');
    });
    
    // Add active class to selected variant
    element.classList.add('active');
    
    // Get all durations for this variant
    const variantId = element.dataset.variantId;
    const availableDurations = getAvailableDurations(variantId);
    
    // Update duration options
    document.querySelectorAll('.duration-option').forEach(option => {
        const duration = parseInt(option.dataset.duration);
        if (availableDurations.includes(duration)) {
            option.classList.remove('disabled');
        } else {
            option.classList.add('disabled');
        }
    });

    // Select first available duration
    const firstAvailableDuration = document.querySelector('.duration-option:not(.disabled)');
    if (firstAvailableDuration) {
        selectDuration(firstAvailableDuration);
    }
}

function selectDuration(element) {
    if (element.classList.contains('disabled')) return;
    
    // Remove active class from all durations
    document.querySelectorAll('.duration-option').forEach(el => {
        el.classList.remove('active');
    });
    
    // Add active class to selected duration
    element.classList.add('active');
    
    // Update price
    updatePrice();
}

function getAvailableDurations(variantId) {
    // Implement this function to return array of available durations for the variant
    // For now, return all durations
    return Array.from(document.querySelectorAll('.duration-option'))
        .map(option => parseInt(option.dataset.duration));
}

function updateDurationOptions(variantId) {
    const durationOptions = document.querySelectorAll('.duration-option');
    let firstEnabled = true;
    
    durationOptions.forEach(option => {
        const isAvailable = checkDurationAvailability(variantId, option.dataset.duration);
        option.classList.toggle('disabled', !isAvailable);
        
        if (isAvailable && firstEnabled) {
            option.click();
            firstEnabled = false;
        }
    });
}

function checkDurationAvailability(variantId, duration) {
    // Kiểm tra xem duration có available cho variant này không
    // Bạn cần implement logic này dựa trên data của bạn
    return true; // Temporary return true
}

function updatePrice() {
    const activeVariant = document.querySelector('.variant-option.active');
    const activeDuration = document.querySelector('.duration-option.active:not(.hidden)');
    
    if (!activeVariant || !activeDuration) return;

    const price = parseFloat(activeDuration.dataset.price);
    const formattedPrice = new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price);

    document.querySelector('.current-price').textContent = formattedPrice;
    document.querySelector('.current-price').dataset.price = price;
    
    updateTotalPrice();
}

function updateTotalPrice() {
    const basePrice = parseFloat(document.querySelector('.current-price').dataset.price);
    const checkedProducts = document.querySelectorAll('.cross-sale-checkbox:checked');
    
    let totalPrice = basePrice;
    checkedProducts.forEach(checkbox => {
        const productPrice = parseFloat(checkbox.dataset.price);
        const discount = parseFloat(checkbox.dataset.discount);
        totalPrice += productPrice * (1 - discount / 100);
    });

    document.querySelector('.total-price').textContent = new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(totalPrice);
} 
} 