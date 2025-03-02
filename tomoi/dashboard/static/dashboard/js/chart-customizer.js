/**
 * Thêm tính năng tùy chỉnh màu sắc cho biểu đồ trong báo cáo bảo hành
 */
$(document).ready(function() {
    // Khởi tạo màu mặc định
    const defaultColors = {
        primary: '#4e73df',
        secondary: '#1cc88a',
        accent: '#f6c23e',
        danger: '#e74a3b',
        dark: '#5a5c69'
    };
    
    // Thêm panel điều khiển màu sắc vào trang
    const colorControls = `
        <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Tùy chỉnh màu sắc biểu đồ</h6>
                <div class="dropdown no-arrow">
                    <a class="dropdown-toggle" href="#" role="button" id="colorDropdown" 
                       data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                    </a>
                    <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" 
                         aria-labelledby="colorDropdown">
                        <a class="dropdown-item" href="#" id="resetColors">Đặt lại màu mặc định</a>
                        <a class="dropdown-item" href="#" id="saveColorScheme">Lưu bộ màu</a>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label>Màu chính</label>
                        <div id="primaryColorPicker" class="color-picker" style="background-color: ${defaultColors.primary}"></div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label>Màu phụ</label>
                        <div id="secondaryColorPicker" class="color-picker" style="background-color: ${defaultColors.secondary}"></div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label>Màu nhấn</label>
                        <div id="accentColorPicker" class="color-picker" style="background-color: ${defaultColors.accent}"></div>
                    </div>
                </div>
                <button id="applyColors" class="btn btn-primary btn-sm">Áp dụng màu sắc</button>
            </div>
        </div>
    `;
    
    // Thêm controls vào vị trí thích hợp trong trang
    $('#colorControlsContainer').html(colorControls);
    
    // Khởi tạo color pickers
    initializeColorPickers();
    
    // Xử lý sự kiện áp dụng màu sắc
    $('#applyColors').on('click', function() {
        updateChartColors();
    });
    
    // Xử lý đặt lại màu mặc định
    $('#resetColors').on('click', function() {
        $('#primaryColorPicker').css('background-color', defaultColors.primary);
        $('#secondaryColorPicker').css('background-color', defaultColors.secondary);
        $('#accentColorPicker').css('background-color', defaultColors.accent);
        updateChartColors();
    });
    
    // Lưu bộ màu vào localStorage
    $('#saveColorScheme').on('click', function() {
        const colorScheme = {
            primary: $('#primaryColorPicker').css('background-color'),
            secondary: $('#secondaryColorPicker').css('background-color'),
            accent: $('#accentColorPicker').css('background-color')
        };
        
        localStorage.setItem('chartColorScheme', JSON.stringify(colorScheme));
        alert('Đã lưu bộ màu thành công!');
    });
    
    // Tải bộ màu từ localStorage nếu có
    const savedColorScheme = localStorage.getItem('chartColorScheme');
    if (savedColorScheme) {
        try {
            const colors = JSON.parse(savedColorScheme);
            $('#primaryColorPicker').css('background-color', colors.primary);
            $('#secondaryColorPicker').css('background-color', colors.secondary);
            $('#accentColorPicker').css('background-color', colors.accent);
            updateChartColors();
        } catch (e) {
            console.error('Lỗi khi tải bộ màu:', e);
        }
    }
}); 