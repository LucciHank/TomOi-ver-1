/**
 * Quản lý theme màu sắc cho biểu đồ
 */
class ChartThemeManager {
    constructor() {
        this.themes = {
            default: {
                primary: '#4e73df',
                secondary: '#1cc88a',
                accent: '#f6c23e',
                danger: '#e74a3b',
                dark: '#5a5c69'
            },
            dark: {
                primary: '#375fd8',
                secondary: '#10a06c',
                accent: '#e8b526',
                danger: '#d32f20',
                dark: '#3a3b45'
            },
            pastel: {
                primary: '#7986cb',
                secondary: '#81c784',
                accent: '#ffb74d',
                danger: '#e57373',
                dark: '#90a4ae'
            },
            contrast: {
                primary: '#000080',
                secondary: '#006400',
                accent: '#b8860b',
                danger: '#8b0000',
                dark: '#2f4f4f'
            }
        };
        
        this.currentTheme = 'default';
    }
    
    // Lấy màu từ theme hiện tại
    getColors() {
        return this.themes[this.currentTheme];
    }
    
    // Áp dụng theme cho tất cả các biểu đồ
    applyTheme(themeName) {
        if (!this.themes[themeName]) return;
        
        this.currentTheme = themeName;
        const colors = this.getColors();
        
        // Cập nhật giao diện color picker
        $('#primaryColorPicker').css('background-color', colors.primary);
        $('#secondaryColorPicker').css('background-color', colors.secondary);
        $('#accentColorPicker').css('background-color', colors.accent);
        
        // Kích hoạt cập nhật biểu đồ
        if (typeof updateChartColors === 'function') {
            updateChartColors();
        }
        
        // Lưu cài đặt
        localStorage.setItem('chartTheme', themeName);
    }
    
    // Áp dụng màu tùy chỉnh
    applyCustomColors(colors) {
        const customTheme = {
            primary: colors.primary || this.themes.default.primary,
            secondary: colors.secondary || this.themes.default.secondary,
            accent: colors.accent || this.themes.default.accent,
            danger: this.themes.default.danger,
            dark: this.themes.default.dark
        };
        
        this.themes.custom = customTheme;
        this.currentTheme = 'custom';
        
        // Lưu cài đặt
        localStorage.setItem('chartCustomTheme', JSON.stringify(customTheme));
        localStorage.setItem('chartTheme', 'custom');
    }
    
    // Khởi tạo từ localStorage
    initialize() {
        // Tải theme đã lưu
        const savedTheme = localStorage.getItem('chartTheme');
        const savedCustomTheme = localStorage.getItem('chartCustomTheme');
        
        if (savedCustomTheme) {
            try {
                this.themes.custom = JSON.parse(savedCustomTheme);
            } catch (e) {
                console.error('Lỗi khi tải theme tùy chỉnh:', e);
            }
        }
        
        if (savedTheme) {
            this.applyTheme(savedTheme);
        }
    }
}

// Khởi tạo và gán vào window để sử dụng toàn cục
window.chartThemeManager = new ChartThemeManager();

$(document).ready(function() {
    // Khởi tạo từ cài đặt đã lưu
    window.chartThemeManager.initialize();
    
    // Thêm nút chọn theme vào giao diện quản lý màu sắc
    $('#colorControlsContainer .card-body').append(`
        <div class="mt-3">
            <label>Chọn nhanh theme:</label>
            <div class="btn-group btn-group-sm" role="group">
                <button type="button" class="btn btn-outline-primary theme-btn" data-theme="default">Mặc định</button>
                <button type="button" class="btn btn-outline-dark theme-btn" data-theme="dark">Tối</button>
                <button type="button" class="btn btn-outline-info theme-btn" data-theme="pastel">Pastel</button>
                <button type="button" class="btn btn-outline-secondary theme-btn" data-theme="contrast">Tương phản cao</button>
            </div>
        </div>
    `);
    
    // Xử lý sự kiện khi chọn theme
    $('.theme-btn').on('click', function() {
        const themeName = $(this).data('theme');
        window.chartThemeManager.applyTheme(themeName);
    });
}); 