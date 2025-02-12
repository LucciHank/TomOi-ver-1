function filterWishlist() {
    const form = document.getElementById('filterForm');
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);

    // Thêm params vào URL nhưng không reload trang
    window.history.pushState({}, '', `${window.location.pathname}?${params}`);

    fetch(`${window.location.pathname}?${params}`)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newProducts = doc.getElementById('wishlistProducts');

            if (newProducts) {
                document.getElementById('wishlistProducts').innerHTML = newProducts.innerHTML;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function resetFilter() {
    const form = document.getElementById('filterForm');
    form.reset();
    filterWishlist();
}

// Thêm debounce cho input search
let searchTimeout;
document.querySelector('input[name="search"]').addEventListener('input', function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(filterWishlist, 500);
});

// Tự động filter khi thay đổi select
document.querySelectorAll('select').forEach(select => {
    select.addEventListener('change', filterWishlist);
});

function toggleWishlist(button, event) {
    event.preventDefault();
    event.stopPropagation();

    // Hiện dialog xác nhận
    Swal.fire({
        title: 'Xóa khỏi danh sách yêu thích?',
        text: 'Bạn có chắc chắn muốn xóa sản phẩm này khỏi mục danh sách yêu thích?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#df2626',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            const productId = button.dataset.productId;
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/store/toggle-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    product_id: productId
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'removed') {
                        // Xóa card sản phẩm với animation
                        const productCard = button.closest('.product-card');
                        productCard.style.transition = 'all 0.3s ease';
                        productCard.style.opacity = '0';
                        productCard.style.transform = 'translateX(100px)';

                        setTimeout(() => {
                            productCard.remove();

                            // Cập nhật số lượng sản phẩm
                            const countElement = document.querySelector('.wishlist-count');
                            const currentCount = parseInt(countElement.textContent);
                            countElement.textContent = `${currentCount - 1} sản phẩm`;

                            // Nếu không còn sản phẩm nào, hiển thị empty state
                            if (currentCount - 1 === 0) {
                                const wishlistGrid = document.querySelector('.products-grid');
                                wishlistGrid.innerHTML = `
                                <div class="empty-wishlist">
                                    <i class="far fa-heart"></i>
                                    <p>Bạn chưa có sản phẩm yêu thích nào</p>
                                </div>
                            `;
                            }
                        }, 300);
                    }

                    Swal.fire({
                        text: data.message,
                        icon: 'success',
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        text: 'Có lỗi xảy ra',
                        icon: 'error',
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000
                    });
                });
        }
    });
} 