document.addEventListener('DOMContentLoaded', function() {
    // Xử lý preview avatar
    function previewAvatar(input) {
        if (input.files && input.files[0]) {
            // Kiểm tra kích thước file
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

    // Xử lý mở modal khi click nút chỉnh sửa
    const editButton = document.querySelector('.btn-danger');
    if (editButton) {
        editButton.addEventListener('click', function() {
            const editModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
            editModal.show();
        });
    }

    // Xử lý form submit
    const editProfileForm = document.getElementById('editProfileForm');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(updateProfileUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert(data.message || 'Có lỗi xảy ra');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi cập nhật thông tin');
            });
        });
    }
}); 