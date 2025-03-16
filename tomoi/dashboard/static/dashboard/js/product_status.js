/**
 * Product Status Management
 * 
 * Xử lý chức năng cập nhật trạng thái sản phẩm từ active sang inactive và ngược lại
 */

$(document).ready(function () {
    // Xử lý nút chuyển đổi trạng thái
    $('.toggle-product-status').on('click', function (e) {
        e.preventDefault();

        const productId = $(this).data('product-id');
        const statusSwitch = $(this);
        const currentStatus = statusSwitch.is(':checked');
        const csrfToken = $('meta[name="csrf-token"]').attr('content');

        // Hiển thị thông báo xác nhận
        const statusText = currentStatus ? 'kích hoạt' : 'vô hiệu hóa';
        if (!confirm(`Bạn có chắc chắn muốn ${statusText} sản phẩm này?`)) {
            // Nếu người dùng hủy, đảo ngược trạng thái của nút chuyển đổi
            statusSwitch.prop('checked', !currentStatus);
            return;
        }

        // Hiển thị loading
        const loadingOverlay = $('<div class="loading-overlay"><div class="spinner-border text-primary" role="status"><span class="sr-only">Đang xử lý...</span></div></div>');
        $('body').append(loadingOverlay);

        // Gửi yêu cầu AJAX để cập nhật trạng thái
        $.ajax({
            url: `/dashboard/products/${productId}/update-status/`,
            type: 'POST',
            data: {
                csrfmiddlewaretoken: csrfToken
            },
            success: function (response) {
                if (response.success) {
                    // Cập nhật giao diện
                    const statusCell = statusSwitch.closest('tr').find('.product-status');
                    if (response.is_active) {
                        statusCell.html('<span class="badge badge-success">Đang bán</span>');
                    } else {
                        statusCell.html('<span class="badge badge-secondary">Tạm dừng</span>');
                    }

                    // Hiển thị thông báo thành công
                    toastr.success(response.message);
                } else {
                    // Đảo ngược trạng thái nút chuyển đổi nếu có lỗi
                    statusSwitch.prop('checked', !currentStatus);
                    toastr.error(response.message || 'Có lỗi xảy ra khi cập nhật trạng thái.');
                }
            },
            error: function (xhr) {
                // Đảo ngược trạng thái nút chuyển đổi
                statusSwitch.prop('checked', !currentStatus);

                // Hiển thị thông báo lỗi
                let errorMsg = 'Có lỗi xảy ra khi cập nhật trạng thái.';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMsg = xhr.responseJSON.message;
                }
                toastr.error(errorMsg);
            },
            complete: function () {
                // Ẩn loading
                loadingOverlay.remove();
            }
        });
    });
}); 