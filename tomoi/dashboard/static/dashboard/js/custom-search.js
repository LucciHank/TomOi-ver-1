// Tìm kiếm realtime
$(document).ready(function() {
    // Danh sách chức năng
    const features = [
        { id: 1, title: "Tổng quan", url: "/dashboard/", description: "Xem thông tin tổng quan" },
        { id: 2, title: "Quản lý người dùng", url: "/dashboard/users/", description: "Quản lý tài khoản người dùng" },
        { id: 3, title: "Quản lý sản phẩm", url: "/dashboard/products/", description: "Quản lý kho sản phẩm" },
        { id: 4, title: "Quản lý đơn hàng", url: "/dashboard/orders/", description: "Quản lý đơn hàng" },
        { id: 5, title: "Cài đặt hệ thống", url: "/dashboard/settings/", description: "Thiết lập cấu hình hệ thống" },
        { id: 6, title: "Báo cáo & thống kê", url: "/dashboard/reports/", description: "Xem báo cáo hoạt động" },
        { id: 7, title: "Marketing", url: "/dashboard/marketing/", description: "Quản lý chiến dịch marketing" }
    ];

    // Hiển thị dropdown khi focus vào ô tìm kiếm
    $("#globalSearch").on("focus", function() {
        $("#searchResults").show();
    });

    // Ẩn dropdown khi click ra ngoài
    $(document).on("click", function(event) {
        if (!$(event.target).closest("#globalSearch, #searchResults").length) {
            $("#searchResults").hide();
        }
    });

    // Xử lý tìm kiếm realtime
    $("#globalSearch").on("keyup", function() {
        const searchTerm = $(this).val().toLowerCase();
        
        if (searchTerm.length < 2) {
            // Nếu nhập ít hơn 2 ký tự, hiển thị các chức năng phổ biến
            showPopularFeatures();
            return;
        }
        
        // Tìm trong danh sách chức năng
        const matchedFeatures = features.filter(feature => 
            feature.title.toLowerCase().includes(searchTerm) || 
            feature.description.toLowerCase().includes(searchTerm)
        );
        
        // Hiển thị kết quả tìm kiếm chức năng
        displayFeatureResults(matchedFeatures, searchTerm);
        
        // AJAX để tìm kiếm trong dữ liệu 
        searchUsers(searchTerm);
        searchProducts(searchTerm);
        searchOrders(searchTerm);
    });

    // Hiển thị các chức năng phổ biến
    function showPopularFeatures() {
        const popularFeatures = features.slice(0, 4); // Lấy 4 chức năng đầu tiên
        displayFeatureResults(popularFeatures, "");
        
        // Xóa kết quả tìm kiếm khác
        $("#userResults, #productResults, #orderResults").empty();
    }

    // Hiển thị kết quả tìm kiếm chức năng
    function displayFeatureResults(results, searchTerm) {
        const resultsContainer = $("#featureResults");
        resultsContainer.empty();
        
        if (results.length === 0) {
            resultsContainer.html('<div class="p-3 text-center text-muted">Không tìm thấy chức năng phù hợp</div>');
            return;
        }
        
        results.forEach(feature => {
            const title = highlightText(feature.title, searchTerm);
            const description = highlightText(feature.description, searchTerm);
            
            resultsContainer.append(`
                <a href="${feature.url}" class="dropdown-item search-result-item">
                    <div class="search-result-title">${title}</div>
                    <div class="search-result-description">${description}</div>
                </a>
            `);
        });
    }

    // Tìm kiếm người dùng
    function searchUsers(searchTerm) {
        $.ajax({
            url: "/dashboard/users/search/",
            type: "GET",
            data: { q: searchTerm },
            success: function(data) {
                displayUserResults(data.users, searchTerm);
            },
            error: function() {
                $("#userResults").html('<div class="p-3 text-center text-muted">Lỗi khi tìm kiếm người dùng</div>');
            }
        });
    }

    // Hiển thị kết quả tìm kiếm người dùng
    function displayUserResults(users, searchTerm) {
        const resultsContainer = $("#userResults");
        resultsContainer.empty();
        
        if (!users || users.length === 0) {
            resultsContainer.html('<div class="p-3 text-center text-muted">Không tìm thấy người dùng phù hợp</div>');
            return;
        }
        
        users.slice(0, 3).forEach(user => { // Chỉ hiển thị tối đa 3 kết quả
            const username = highlightText(user.username, searchTerm);
            const email = highlightText(user.email, searchTerm);
            
            resultsContainer.append(`
                <a href="/dashboard/users/${user.id}/" class="dropdown-item search-result-item">
                    <div class="search-result-title">${username}</div>
                    <div class="search-result-description">${email}</div>
                </a>
            `);
        });
        
        if (users.length > 3) {
            resultsContainer.append(`
                <a href="/dashboard/users/?search=${searchTerm}" class="dropdown-item text-center small">
                    + ${users.length - 3} người dùng khác
                </a>
            `);
        }
    }

    // Tìm kiếm sản phẩm (tương tự như tìm người dùng)
    function searchProducts(searchTerm) {
        // Mã tương tự như searchUsers
    }

    // Tìm kiếm đơn hàng (tương tự như tìm người dùng)
    function searchOrders(searchTerm) {
        // Mã tương tự như searchUsers
    }

    // Hàm highlight từ khóa tìm kiếm
    function highlightText(text, searchTerm) {
        if (!searchTerm) return text;
        
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<span class="search-highlight">$1</span>');
    }

    // Khởi tạo ban đầu: hiển thị các chức năng phổ biến
    showPopularFeatures();
}); 