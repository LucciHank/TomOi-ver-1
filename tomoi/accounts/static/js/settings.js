const DEEPL_API_KEY = '893c70b4-e735-4e1c-b9cd-e27585166d17:fx';

// Định nghĩa ngôn ngữ được hỗ trợ và mã ngôn ngữ tương ứng cho DeepL
const SUPPORTED_LANGUAGES = {
    'vi': 'VI',
    'en': 'EN',
};

// Cache để lưu các bản dịch
const translationCache = new Map();

// Hàm dịch text sử dụng backend endpoint
async function translateText(text, targetLang) {
    const cacheKey = `${text}_${targetLang}`;
    if (translationCache.has(cacheKey)) {
        return translationCache.get(cacheKey);
    }

    try {
        const response = await fetch('/accounts/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                text: text,
                target_lang: SUPPORTED_LANGUAGES[targetLang]
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Translation failed');
        }

        const data = await response.json();
        if (data.success) {
            translationCache.set(cacheKey, data.translation);
            return data.translation;
        } else {
            throw new Error(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        throw error;
    }
}

// Hàm chuyển đổi ngôn ngữ
async function changeLanguage(lang) {
    // Hiển thị loading dialog
    const loadingDialog = Swal.fire({
        title: 'Đang chuyển đổi ngôn ngữ...',
        allowOutsideClick: false,
        showConfirmButton: false,
        willOpen: () => {
            Swal.showLoading();
        }
    });

    try {
        // Lấy tất cả các phần tử cần dịch
        const elements = document.querySelectorAll('[data-translate="true"]');

        // Dịch từng phần tử
        for (const element of elements) {
            const originalText = element.getAttribute('data-original-text') || element.textContent.trim();

            // Lưu text gốc nếu chưa có
            if (!element.getAttribute('data-original-text')) {
                element.setAttribute('data-original-text', originalText);
            }

            // Nếu chọn tiếng Việt, sử dụng text gốc
            if (lang === 'vi') {
                element.textContent = originalText;
            } else {
                // Dịch sang ngôn ngữ khác
                const translatedText = await translateText(originalText, lang);
                element.textContent = translatedText;
            }
        }

        // Cập nhật trạng thái active cho nút ngôn ngữ
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.lang === lang) {
                btn.classList.add('active');
            }
        });

        // Lưu ngôn ngữ đã chọn
        localStorage.setItem('selectedLanguage', lang);

        // Đóng loading dialog và hiển thị thông báo thành công
        loadingDialog.close();
        await Swal.fire({
            icon: 'success',
            title: 'Thành công!',
            text: 'Đã chuyển đổi ngôn ngữ thành công',
            timer: 2000,
            showConfirmButton: false
        });

    } catch (error) {
        console.error('Error changing language:', error);
        loadingDialog.close();
        await Swal.fire({
            icon: 'error',
            title: 'Lỗi!',
            text: error.message || 'Không thể chuyển đổi ngôn ngữ. Vui lòng thử lại sau.',
            confirmButtonText: 'Đóng'
        });
    }
}

// Khởi tạo khi trang load xong
document.addEventListener('DOMContentLoaded', function () {
    // Khôi phục ngôn ngữ đã lưu
    const savedLang = localStorage.getItem('selectedLanguage');
    if (savedLang && SUPPORTED_LANGUAGES[savedLang]) {
        const buttons = document.querySelectorAll('.lang-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.lang === savedLang) {
                btn.classList.add('active');
            }
        });
        changeLanguage(savedLang);
    }

    // Xử lý click cho các nút ngôn ngữ
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            if (window.changeLanguage) {
                window.changeLanguage(this.dataset.lang);
            } else {
                console.error('changeLanguage function not found');
            }
        });
    });
});