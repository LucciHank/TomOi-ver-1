document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[type="file"]').forEach(function (fileInput) {
        fileInput.addEventListener('change', function () {
            const files = fileInput.files;
            const preview = document.createElement('div');
            for (let i = 0; i < files.length; i++) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(files[i]);
                img.height = 60;
                preview.appendChild(img);
            }
            fileInput.parentNode.appendChild(preview);
        });
    });
});
