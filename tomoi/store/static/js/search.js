document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('.search-input');
    const searchSuggestions = document.querySelector('.search-suggestions');
    let debounceTimer;

    // Hiển thị gợi ý khi focus vào input
    searchInput.addEventListener('focus', function () {
        // Nếu đã có dữ liệu từ trước, hiển thị luôn
        if (searchSuggestions.innerHTML.trim()) {
            searchSuggestions.style.display = 'block';
        } else {
            // Nếu chưa có dữ liệu, hiển thị một số gợi ý phổ biến
            showPopularSuggestions();
        }
    });

    // Ẩn gợi ý khi click ra ngoài
    document.addEventListener('click', function (event) {
        if (!searchInput.contains(event.target) && !searchSuggestions.contains(event.target)) {
            searchSuggestions.style.display = 'none';
        }
    });

    // Xử lý khi người dùng nhập
    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length >= 2) {
            debounceTimer = setTimeout(function () {
                fetchSuggestions(query);
            }, 300);
        } else if (query.length === 0) {
            // Nếu không có query, hiển thị gợi ý phổ biến
            showPopularSuggestions();
        } else {
            searchSuggestions.style.display = 'none';
        }
    });

    // Hàm hiển thị gợi ý phổ biến
    function showPopularSuggestions() {
        searchSuggestions.innerHTML = `
            <div class="suggestion-header">Tìm kiếm phổ biến</div>
            <ul class="suggestion-list">
                <li class="suggestion-item"><a href="/search?q=netflix">Netflix</a></li>
                <li class="suggestion-item"><a href="/search?q=spotify">Spotify</a></li>
                <li class="suggestion-item"><a href="/search?q=office">Office 365</a></li>
                <li class="suggestion-item"><a href="/search?q=windows">Windows</a></li>
                <li class="suggestion-item"><a href="/search?q=chatgpt">ChatGPT</a></li>
            </ul>
        `;
        searchSuggestions.style.display = 'block';
    }

    // Hàm lấy gợi ý từ server
    function fetchSuggestions(query) {
        fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.suggestions && data.suggestions.length > 0) {
                    displaySuggestions(data.suggestions);
                } else {
                    // Nếu không có kết quả phù hợp
                    searchSuggestions.innerHTML = `
                        <div class="suggestion-header">Gợi ý tìm kiếm</div>
                        <div class="no-suggestions">Không tìm thấy kết quả phù hợp</div>
                    `;
                    searchSuggestions.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
                // Trong trường hợp lỗi, hiển thị gợi ý mặc định
                showPopularSuggestions();
            });
    }

    // Hàm hiển thị gợi ý
    function displaySuggestions(suggestions) {
        let html = `<div class="suggestion-header">Gợi ý tìm kiếm</div>
                   <ul class="suggestion-list">`;

        suggestions.forEach(item => {
            html += `<li class="suggestion-item">
                     <a href="/product/${item.slug}">
                       <div class="suggestion-product">
                         <img src="${item.image}" alt="${item.name}" class="suggestion-image">
                         <div class="suggestion-info">
                           <div class="suggestion-name">${item.name}</div>
                           <div class="suggestion-price">${item.price}</div>
                         </div>
                       </div>
                     </a>
                   </li>`;
        });

        html += `</ul>`;

        searchSuggestions.innerHTML = html;
        searchSuggestions.style.display = 'block';
    }

    // Xử lý khi form tìm kiếm được submit
    document.querySelector('.search-form').addEventListener('submit', function (event) {
        const query = searchInput.value.trim();
        if (query.length === 0) {
            event.preventDefault();
        }
    });
}); 