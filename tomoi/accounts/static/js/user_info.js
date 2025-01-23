document.addEventListener('DOMContentLoaded', function() {
    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    
    // Xử lý preview avatar
    function previewAvatar(input) {
        if (input.files && input.files[0]) {
            const maxSize = 5 * 1024 * 1024; // 5MB
            if (input.files[0].size > maxSize) {
                alert('Kích thước ảnh không được vượt quá 5MB');
                input.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                const previewImg = document.querySelector('.preview-avatar');
                if (previewImg) {
                    previewImg.src = e.target.result;
                }
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Gán sự kiện cho input file
    const avatarInput = document.querySelector('input[name="avatar"]');
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            previewAvatar(this);
        });
    }

    // Xử lý form submit
    const editProfileForm = document.getElementById('editProfileForm');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                const formData = new FormData(this);
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                const response = await fetch(updateProfileUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin'
                });

                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Server response was not JSON');
                }

                const data = await response.json();
                
                if (response.ok && data.success) {
                    // Đóng modal
                    editProfileModal.hide();
                    
                    // Hiển thị thông báo thành công
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công!',
                        text: data.message || 'Cập nhật thông tin thành công',
                        showConfirmButton: false,
                        timer: 1500
                    }).then(() => {
                        // Reload trang sau khi thông báo đóng
                        window.location.reload();
                    });
                } else {
                    throw new Error(data.message || 'Có lỗi xảy ra');
                }
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Lỗi!',
                    text: error.message || 'Có lỗi xảy ra khi cập nhật thông tin'
                });
            }
        });
    }
}); 