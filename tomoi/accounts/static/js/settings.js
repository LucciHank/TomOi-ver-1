document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings JS loaded');
    
    // Debug các element
    console.log('Language buttons:', document.querySelectorAll('.language-toggle button'));
    console.log('Theme inputs:', document.querySelectorAll('input[name="theme"]'));
    console.log('Snow effect:', document.getElementById('snowEffect'));
    console.log('Pet effect:', document.getElementById('petEffect'));
    console.log('Font size inputs:', document.querySelectorAll('input[name="fontSize"]'));
    
    // Detect ngôn ngữ trình duyệt
    const userLang = navigator.language.split('-')[0];
    const savedLang = localStorage.getItem('language') || 
                     (['vi', 'en'].includes(userLang) ? userLang : 'vi');
    
    // Cập nhật UI theo ngôn ngữ đã lưu
    document.querySelectorAll('.language-toggle button').forEach(button => {
        if(button.dataset.language === savedLang) {
            button.classList.add('active');
        }
        
        button.addEventListener('click', function() {
            const language = this.dataset.language;
            updateLanguage(language);
        });
    });

    // Xử lý chuyển đổi theme
    document.querySelectorAll('input[name="theme"]').forEach(input => {
        input.addEventListener('change', function() {
            updateTheme(this.value);
        });
    });

    // Xử lý hiệu ứng
    document.getElementById('snowEffect').addEventListener('change', function() {
        toggleSnowEffect(this.checked);
    });

    document.getElementById('petEffect').addEventListener('change', function() {
        togglePetEffect(this.checked);
    });

    // Xử lý cỡ chữ
    document.querySelectorAll('input[name="fontSize"]').forEach(input => {
        input.addEventListener('change', function() {
            updateFontSize(this.value);
        });
    });
});

// Các hàm xử lý
function updateLanguage(language) {
    // Hiển thị loading
    Swal.fire({
        title: 'Đang cập nhật...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    // Kích hoạt Google Translate
    changeLanguage(language);
    
    // Đóng loading sau 1 giây
    setTimeout(() => {
        Swal.fire({
            icon: 'success',
            title: language === 'vi' ? 'Đã cập nhật ngôn ngữ!' : 'Language updated!',
            timer: 1500,
            showConfirmButton: false
        });
    }, 1000);
}

function updateTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

function toggleSnowEffect(enabled) {
    if (enabled) {
        startSnowEffect();
    } else {
        stopSnowEffect();
    }
    localStorage.setItem('snowEffect', enabled);
}

function togglePetEffect(enabled) {
    if (enabled) {
        startPetEffect();
    } else {
        stopPetEffect();
    }
    localStorage.setItem('petEffect', enabled);
}

function updateFontSize(size) {
    document.documentElement.setAttribute('data-font-size', size);
    localStorage.setItem('fontSize', size);
}

// Hiệu ứng tuyết rơi
function startSnowEffect() {
    // Code xử lý hiệu ứng tuyết rơi
}

function stopSnowEffect() {
    // Code dừng hiệu ứng tuyết rơi
}

// Hiệu ứng pet mini
function startPetEffect() {
    // Code xử lý hiệu ứng pet mini
}

function stopPetEffect() {
    // Code dừng hiệu ứng pet mini
} 