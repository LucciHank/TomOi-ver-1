// Search Suggestions
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const suggestionsContainer = document.querySelector('.search-suggestions');
    let debounceTimer;

    // Debug logs
    console.log('Search form:', document.querySelector('.search-form'));
    console.log('Search input:', searchInput);
    console.log('Suggestions container:', suggestionsContainer);
    
    if (!searchInput || !suggestionsContainer) {
        console.error('Search elements not found!');
        return;
    }

    // Show trending on focus
    searchInput.addEventListener('focus', function() {
        console.log('Search input focused');
        if (!this.value.trim()) {
            fetch('/api/search-suggestions/trending/')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log('Trending data:', data);
                    showSuggestions(data.suggestions);
                })
                .catch(error => console.error('Error fetching trending:', error));
        }
    });

    // Handle input with debounce
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        
        if (query.length < 1) {
            suggestionsContainer.classList.remove('show');
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log('Search response:', data);
                    showSuggestions(data.suggestions);
                })
                .catch(error => console.error('Error fetching suggestions:', error));
        }, 300);
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.classList.remove('show');
        }
    });

    function showSuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            suggestionsContainer.classList.remove('show');
            return;
        }

        suggestionsContainer.innerHTML = suggestions.map(item => {
            if (item.type === 'trending' || item.type === 'product') {
                return `
                    <a href="/search/?q=${encodeURIComponent(item.keyword)}" 
                       class="suggestion-item ${item.type}">
                        <i class="${item.icon}"></i>
                        <span>${item.keyword}</span>
                        ${item.count ? `<small>${item.count} lượt tìm</small>` : ''}
                    </a>
                `;
            } else {
                return `
                    <a href="${item.url}" class="suggestion-item">
                        <img src="${item.image}" alt="${item.name}">
                        <div class="suggestion-info">
                            <div class="suggestion-name">${item.name}</div>
                            <div class="suggestion-price">${formatPrice(item.price)}</div>
                        </div>
                    </a>
                `;
            }
        }).join('');
        
        suggestionsContainer.classList.add('show');
    }
});

// Price Range Slider
const rangeInputs = document.querySelectorAll(".range-input");
const priceInputs = document.querySelectorAll(".price-inputs input");
const range = document.querySelector(".slider-track");
let minValue = parseInt(rangeInputs[0].value);
let maxValue = parseInt(rangeInputs[1].value);

// Initialize price inputs
priceInputs[0].value = formatPrice(minValue);
priceInputs[1].value = formatPrice(maxValue);

// Handle range input changes
rangeInputs.forEach(input => {
    input.addEventListener("input", e => {
        minValue = parseInt(rangeInputs[0].value);
        maxValue = parseInt(rangeInputs[1].value);
        
        if(maxValue - minValue < 1000000) {
            if(e.target.classList.contains("min")) {
                rangeInputs[0].value = maxValue - 1000000;
            } else {
                rangeInputs[1].value = minValue + 1000000;
            }
        } else {
            priceInputs[0].value = formatPrice(minValue);
            priceInputs[1].value = formatPrice(maxValue);
            range.style.left = (minValue / rangeInputs[0].max) * 100 + "%";
            range.style.right = 100 - (maxValue / rangeInputs[1].max) * 100 + "%";
        }
    });
});

// Handle price input changes
priceInputs.forEach((input, index) => {
    input.addEventListener("input", e => {
        let value = parseInt(e.target.value.replace(/\D/g, ""));
        
        if(isNaN(value)) {
            value = index === 0 ? 0 : rangeInputs[1].max;
        }
        
        if(index === 0) {
            if(value > maxValue - 1000000) {
                value = maxValue - 1000000;
            }
            rangeInputs[0].value = value;
            range.style.left = (value / rangeInputs[0].max) * 100 + "%";
        } else {
            if(value < minValue + 1000000) {
                value = minValue + 1000000;
            }
            rangeInputs[1].value = value;
            range.style.right = 100 - (value / rangeInputs[1].max) * 100 + "%";
        }
        
        e.target.value = formatPrice(value);
    });
    
    input.addEventListener("keypress", e => {
        if(e.key === "Enter") {
            applyFilters();
        }
    });
});

// Reset filters
function resetFilters() {
    const query = new URLSearchParams(window.location.search).get('q') || '';
    window.location.href = `${window.location.pathname}${query ? '?q=' + query : ''}`;
}

// Category filter
document.querySelectorAll('.category-item').forEach(item => {
    item.addEventListener('click', function() {
        const category = this.dataset.category;
        document.querySelectorAll('.category-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        applyFilters();
    });
});

// Apply Filters
function applyFilters() {
    const category = document.querySelector('.category-item.active').dataset.category;
    const minPrice = parseInt(rangeInputs[0].value);
    const maxPrice = parseInt(rangeInputs[1].value);
    const sort = document.querySelector('input[name="sort"]:checked').value;
    const query = new URLSearchParams(window.location.search).get('q') || '';
    
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (category) params.set('category', category);
    params.set('min_price', minPrice);
    params.set('max_price', maxPrice);
    if (sort) params.set('sort', sort);
    
    window.location.href = `${window.location.pathname}?${params.toString()}`;
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(price);
}

// Initialize
priceInputs[0].value = formatPrice(minValue);
priceInputs[1].value = formatPrice(maxValue); 