document.addEventListener('DOMContentLoaded', function() {
    // Xử lý ngôn ngữ
    const savedLang = localStorage.getItem('selectedLanguage') || 'vi';
    const buttons = document.querySelectorAll('.language-toggle button');
    
    function updateButtons(activeLang) {
        buttons.forEach(btn => {
            if (btn.dataset.language === activeLang) {
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
                btn.classList.add('btn-outline-danger');
            }
        });
    }

    // Khởi tạo trạng thái ban đầu
    updateButtons(savedLang);
    
    // Xử lý click
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const newLang = this.dataset.language;
            const currentLang = localStorage.getItem('selectedLanguage') || 'vi';
            
            if (newLang !== currentLang) {
                updateButtons(newLang);
                localStorage.setItem('selectedLanguage', newLang);
                
                Swal.fire({
                    icon: 'success',
                    title: 'Thành công!',
                    text: 'Đã chuyển đổi ngôn ngữ thành công',
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        });
    });

    // Xử lý theme
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.querySelector(`input[value="${savedTheme}"]`).checked = true;
    applyTheme(savedTheme);

    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const theme = this.value;
            applyTheme(theme);
            localStorage.setItem('theme', theme);
            
            Swal.fire({
                icon: 'success',
                text: 'Đã thay đổi giao diện thành công',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        });
    });
});

function applyTheme(theme) {
    if (theme === 'auto') {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }
        
        window.matchMedia('(prefers-color-scheme: dark)')
            .addEventListener('change', e => {
                document.documentElement.setAttribute('data-theme', 
                    e.matches ? 'dark' : 'light'
                );
            });
    } else {
        document.documentElement.setAttribute('data-theme', theme);
    }
}