/**
 * Xử lý tùy chỉnh màu sắc biểu đồ
 */
function initializeColorPickers() {
    // Khởi tạo các bộ chọn màu
    const pickrOptions = {
        el: '.color-picker',
        theme: 'classic',
        default: '#4e73df',
        swatches: [
            '#4e73df', // Primary
            '#1cc88a', // Success
            '#36b9cc', // Info
            '#f6c23e', // Warning
            '#e74a3b', // Danger
            '#858796'  // Secondary
        ],
        components: {
            preview: true,
            opacity: true,
            hue: true,
            interaction: {
                hex: true,
                rgba: true,
                input: true,
                save: true
            }
        }
    };
    
    // Khởi tạo color picker cho các màu chính
    const primaryPicker = Pickr.create({
        ...pickrOptions,
        el: '#primaryColorPicker',
        default: '#4e73df'
    });
    
    const secondaryPicker = Pickr.create({
        ...pickrOptions,
        el: '#secondaryColorPicker',
        default: '#1cc88a'
    });
    
    const accentPicker = Pickr.create({
        ...pickrOptions,
        el: '#accentColorPicker',
        default: '#f6c23e'
    });
    
    // Xử lý sự kiện thay đổi màu
    primaryPicker.on('save', (color) => {
        const hexColor = color.toHEXA().toString();
        $('#primaryColorPicker').css('background-color', hexColor);
        updateChartColors();
    });
    
    secondaryPicker.on('save', (color) => {
        const hexColor = color.toHEXA().toString();
        $('#secondaryColorPicker').css('background-color', hexColor);
        updateChartColors();
    });
    
    accentPicker.on('save', (color) => {
        const hexColor = color.toHEXA().toString();
        $('#accentColorPicker').css('background-color', hexColor);
        updateChartColors();
    });
}

/**
 * Cập nhật màu sắc cho biểu đồ 
 * @param {Chart} chart - Biểu đồ cần cập nhật
 * @param {string} primaryColor - Mã màu chính
 * @param {string} secondaryColor - Mã màu phụ
 * @param {string} accentColor - Mã màu nhấn mạnh
 */
function applyChartColors(chart, primaryColor, secondaryColor, accentColor) {
    if (!chart || !chart.data || !chart.data.datasets) return;
    
    // Tùy chỉnh theo loại biểu đồ
    if (chart.config.type === 'line' || chart.config.type === 'bar') {
        // Biểu đồ Line hoặc Bar thường có nhiều datasets
        if (chart.data.datasets.length > 0) {
            chart.data.datasets[0].borderColor = primaryColor;
            chart.data.datasets[0].backgroundColor = hexToRgba(primaryColor, 0.2);
        }
        
        if (chart.data.datasets.length > 1) {
            chart.data.datasets[1].borderColor = secondaryColor;
            chart.data.datasets[1].backgroundColor = hexToRgba(secondaryColor, 0.2);
        }
        
        if (chart.data.datasets.length > 2) {
            chart.data.datasets[2].borderColor = accentColor;
            chart.data.datasets[2].backgroundColor = hexToRgba(accentColor, 0.2);
        }
    } 
    else if (chart.config.type === 'pie' || chart.config.type === 'doughnut') {
        // Biểu đồ Pie hoặc Doughnut có mảng màu nền
        chart.data.datasets[0].backgroundColor = [
            primaryColor,
            secondaryColor,
            accentColor,
            hexToRgba(primaryColor, 0.7),
            hexToRgba(secondaryColor, 0.7),
            hexToRgba(accentColor, 0.7)
        ];
    }
    
    // Cập nhật biểu đồ
    chart.update();
}

/**
 * Chuyển đổi mã màu HEX sang RGBA
 * @param {string} hex - Mã màu dạng HEX
 * @param {number} alpha - Độ trong suốt (0-1)
 * @returns {string} - Mã màu dạng RGBA
 */
function hexToRgba(hex, alpha = 1) {
    let r = 0, g = 0, b = 0;
    
    // Kiểm tra định dạng HEX và chuyển đổi
    if (hex.length === 4) {
        r = parseInt(hex[1] + hex[1], 16);
        g = parseInt(hex[2] + hex[2], 16);
        b = parseInt(hex[3] + hex[3], 16);
    } else if (hex.length === 7) {
        r = parseInt(hex.slice(1, 3), 16);
        g = parseInt(hex.slice(3, 5), 16);
        b = parseInt(hex.slice(5, 7), 16);
    }
    
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Hàm công khai để sử dụng từ bên ngoài
window.applyCustomColors = function(chartInstance, colors) {
    applyChartColors(
        chartInstance, 
        colors.primary || '#4e73df', 
        colors.secondary || '#1cc88a', 
        colors.accent || '#f6c23e'
    );
}; 