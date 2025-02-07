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