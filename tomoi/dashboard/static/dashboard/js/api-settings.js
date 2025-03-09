// API Settings JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Lấy form và button
    const apiForm = document.getElementById('api-form');
    const saveApiBtn = document.getElementById('save-api-config');
    const testApiBtn = document.getElementById('test-api-connection');
    const apiStatusIndicator = document.getElementById('api-status');
    
    // Hiển thị/ẩn mật khẩu
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.closest('.input-group').querySelector('input');
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    });
    
    // Kiểm tra kết nối API
    if (testApiBtn) {
        testApiBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Xác định URL dựa trên context
            const testApiUrl = window.location.pathname.includes('/chatbot/') 
                ? '/dashboard/chatbot/api/test/' 
                : '/dashboard/settings/api/test/';
            
            const apiType = document.getElementById('api_type').value;
            const apiKey = document.getElementById('api_key').value;
            const model = document.getElementById('model').value;
            const endpoint = document.getElementById('endpoint')?.value || '';
            
            if (!apiKey) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Vui lòng nhập API Key'
                });
                return;
            }
            
            // Hiển thị trạng thái đang kiểm tra
            apiStatusIndicator.innerHTML = '<span class="text-warning"><i class="fas fa-spinner fa-spin"></i> Đang kiểm tra kết nối...</span>';
            
            // Gửi yêu cầu kiểm tra API
            fetch(testApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    api_type: apiType,
                    api_key: apiKey,
                    model: model,
                    endpoint: endpoint
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("API test response:", data);
                if (data.success) {
                    apiStatusIndicator.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> Kết nối thành công</span>';
                    
                    // Hiển thị thông báo thành công
                    Swal.fire({
                        icon: 'success',
                        title: 'Kết nối thành công',
                        text: 'API key hoạt động bình thường',
                        showConfirmButton: true
                    });
                } else {
                    apiStatusIndicator.innerHTML = `<span class="text-danger"><i class="fas fa-times-circle"></i> ${data.message}</span>`;
                    
                    // Hiển thị thông báo lỗi
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi kết nối',
                        text: data.message,
                        showConfirmButton: true
                    });
                }
            })
            .catch(error => {
                console.error('Error testing API:', error);
                apiStatusIndicator.innerHTML = '<span class="text-danger"><i class="fas fa-times-circle"></i> Lỗi kết nối</span>';
                
                // Hiển thị thông báo lỗi
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã xảy ra lỗi khi kết nối đến API',
                    showConfirmButton: true
                });
            });
        });
    }
    
    // Lưu cấu hình API
    if (saveApiBtn) {
        saveApiBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Xác định URL dựa trên context
            const saveApiUrl = window.location.pathname.includes('/chatbot/') 
                ? '/dashboard/chatbot/api/save/' 
                : '/dashboard/settings/api/save/';
            
            const apiType = document.getElementById('api_type').value;
            const apiKey = document.getElementById('api_key').value;
            const model = document.getElementById('model').value;
            const temperature = document.getElementById('temperature').value;
            const maxTokens = document.getElementById('max_tokens').value;
            const endpoint = document.getElementById('endpoint')?.value || '';
            
            if (!apiKey) {
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Vui lòng nhập API Key'
                });
                return;
            }
            
            // Hiển thị thông báo đang xử lý
            Swal.fire({
                title: 'Đang lưu...',
                html: 'Vui lòng đợi trong giây lát',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            // Gửi yêu cầu lưu cấu hình
            fetch(saveApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    api_type: apiType,
                    api_key: apiKey,
                    model: model,
                    temperature: temperature,
                    max_tokens: maxTokens,
                    endpoint: endpoint
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("API save response:", data);
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: data.message,
                        showConfirmButton: true
                    }).then(() => {
                        // Cập nhật trạng thái và reload trang để hiển thị thông tin mới
                        apiStatusIndicator.innerHTML = '<span class="text-success"><i class="fas fa-check-circle"></i> Đã kết nối</span>';
                        // Reload trang sau 1 giây
                        setTimeout(() => window.location.reload(), 1000);
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Lỗi',
                        text: data.message,
                        showConfirmButton: true
                    });
                }
            })
            .catch(error => {
                console.error('Error saving API config:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi',
                    text: 'Đã xảy ra lỗi khi lưu cấu hình',
                    showConfirmButton: true
                });
            });
        });
    }
    
    // Utility function để lấy CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}); 