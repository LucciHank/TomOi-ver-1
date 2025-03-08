/**
 * TomOi Dashboard - JavaScript Functions
 * Tệp này chứa tất cả các hàm JavaScript cần thiết cho Dashboard
 */

// Dữ liệu mẫu cho các biểu đồ
const sampleData = {
    revenue: {
        day: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59'],
            data: [150000, 280000, 450000, 620000, 800000, 950000, 1200000]
        },
        week: {
            labels: ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'],
            data: [2500000, 3100000, 2800000, 3500000, 4200000, 3800000, 2900000]
        },
        month: {
            labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
            data: [5000000, 7500000, 8200000, 7800000, 9000000, 12000000, 11500000, 10800000, 13200000, 14500000, 15800000, 18000000]
        },
        quarter: {
            labels: ['Quý 1', 'Quý 2', 'Quý 3', 'Quý 4'],
            data: [20700000, 28800000, 35500000, 48300000]
        },
        year: {
            labels: ['2020', '2021', '2022', '2023', '2024'],
            data: [85000000, 110000000, 133000000, 156000000, 178000000]
        }
    },
    profit: {
        day: {
            profit: [80000, 150000, 250000, 320000, 420000, 500000, 650000],
            cost: [70000, 130000, 200000, 300000, 380000, 450000, 550000]
        },
        week: {
            profit: [1200000, 1500000, 1300000, 1800000, 2200000, 2000000, 1500000],
            cost: [1300000, 1600000, 1500000, 1700000, 2000000, 1800000, 1400000]
        },
        month: {
            profit: [2500000, 3800000, 4100000, 3900000, 4500000, 6000000, 5800000, 5400000, 6600000, 7200000, 7900000, 9000000],
            cost: [2500000, 3700000, 4100000, 3900000, 4500000, 6000000, 5700000, 5400000, 6600000, 7300000, 7900000, 9000000]
        },
        quarter: {
            profit: [10400000, 14400000, 17800000, 24100000],
            cost: [10300000, 14400000, 17700000, 24200000]
        },
        year: {
            profit: [42500000, 55000000, 66500000, 78000000, 89000000],
            cost: [42500000, 55000000, 66500000, 78000000, 89000000]
        }
    },
    order: {
        day: {
            labels: ['Hoàn thành', 'Đang xử lý', 'Đã hủy', 'Chờ thanh toán'],
            data: [25, 15, 5, 8],
            colors: ['#1cc88a', '#4e73df', '#e74a3b', '#f6c23e'],
            hoverColors: ['#169e6e', '#2e59d9', '#c9362a', '#daa520']
        },
        week: {
            labels: ['Hoàn thành', 'Đang xử lý', 'Đã hủy', 'Chờ thanh toán'],
            data: [120, 45, 20, 35],
            colors: ['#1cc88a', '#4e73df', '#e74a3b', '#f6c23e'],
            hoverColors: ['#169e6e', '#2e59d9', '#c9362a', '#daa520']
        },
        month: {
            labels: ['Hoàn thành', 'Đang xử lý', 'Đã hủy', 'Chờ thanh toán'],
            data: [458, 180, 85, 120],
            colors: ['#1cc88a', '#4e73df', '#e74a3b', '#f6c23e'],
            hoverColors: ['#169e6e', '#2e59d9', '#c9362a', '#daa520']
        },
        quarter: {
            labels: ['Hoàn thành', 'Đang xử lý', 'Đã hủy', 'Chờ thanh toán'],
            data: [1250, 520, 230, 350],
            colors: ['#1cc88a', '#4e73df', '#e74a3b', '#f6c23e'],
            hoverColors: ['#169e6e', '#2e59d9', '#c9362a', '#daa520']
        },
        year: {
            labels: ['Hoàn thành', 'Đang xử lý', 'Đã hủy', 'Chờ thanh toán'],
            data: [4580, 1850, 820, 1200],
            colors: ['#1cc88a', '#4e73df', '#e74a3b', '#f6c23e'],
            hoverColors: ['#169e6e', '#2e59d9', '#c9362a', '#daa520']
        }
    },
    calendar: {
        events: [
            {
                id: '1',
                title: 'Gói Premium - user1',
                start: '2024-03-15',
                className: 'event-reminder',
                extendedProps: {
                    type: 'reminder',
                    description: 'Gia hạn gói Premium'
                }
            },
            {
                id: '2',
                title: 'Gói VIP - user2',
                start: '2024-03-20',
                className: 'event-reminder',
                extendedProps: {
                    type: 'reminder',
                    description: 'Gia hạn gói VIP'
                }
            },
            {
                id: '3',
                title: 'Gói Standard - user3',
                start: '2024-04-05',
                className: 'event-reminder',
                extendedProps: {
                    type: 'reminder',
                    description: 'Gia hạn gói Standard'
                }
            },
            {
                id: '4',
                title: 'Họp team Marketing',
                start: '2024-03-25T10:00:00',
                end: '2024-03-25T12:00:00',
                className: 'event-meeting',
                extendedProps: {
                    type: 'meeting',
                    description: 'Thảo luận chiến lược quý 2'
                }
            },
            {
                id: '5',
                title: 'Deadline dự án website',
                start: '2024-04-10',
                className: 'event-deadline',
                extendedProps: {
                    type: 'deadline',
                    description: 'Bàn giao sản phẩm cuối cùng'
                }
            }
        ]
    }
};

// Biến toàn cục cho các biểu đồ và lịch
window.dashboardCharts = {
    revenue: null,
    profit: null,
    order: null
};
window.calendar = null;

// Định nghĩa lớp Tooltip sử dụng Bootstrap
function Tooltip(el, options) {
    this.element = el;
    this.options = options || {};
    $(el).tooltip(options);
    
    this.dispose = function() {
        $(el).tooltip('dispose');
    };
}

/**
 * Khởi tạo lịch
 */
function initCalendar() {
    try {
        const calendarEl = document.getElementById('calendar');
        if (!calendarEl) {
            console.error("Không tìm thấy phần tử lịch");
            return;
        }
        
        window.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'vi',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
            },
            buttonText: {
                today: 'Hôm nay',
                month: 'Tháng',
                week: 'Tuần',
                day: 'Ngày',
                list: 'Danh sách'
            },
            selectable: true,
            selectMirror: true,
            dayMaxEvents: true,
            themeSystem: 'bootstrap',
            eventDisplay: 'block',
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                meridiem: false,
                hour12: false
            },
            
            // Hiển thị dây nối từ ngày có sự kiện
            eventContent: function(info) {
                const colorBadge = `<div class="fc-event-dot" style="background-color:${info.event.backgroundColor}"></div>`;
                
                return {
                    html: 
                    `<div class="fc-event-main">
                        ${colorBadge}
                        <div class="fc-event-title">${info.event.title}</div>
                        ${info.timeText ? `<div class="fc-event-time">${info.timeText}</div>` : ''}
                    </div>`
                };
            },
            
            // Sự kiện khi click vào ngày
            dateClick: function(info) {
                showDayEvents(info.date);
            },
            
            // Sự kiện khi click vào event
            eventClick: function(info) {
                info.jsEvent.preventDefault();
                editEvent(info.event);
            },
            
            // Cập nhật khi kéo thả
            eventDrop: function(info) {
                handleEventChange(info, 'Di chuyển sự kiện');
            },
            
            // Cập nhật khi thay đổi kích thước
            eventResize: function(info) {
                handleEventChange(info, 'Thay đổi thời gian sự kiện');
            },
            
            // Hiển thị tooltip
            eventDidMount: function(info) {
                // Thêm tooltip
                new Tooltip(info.el, {
                    title: getEventTooltipContent(info.event),
                    html: true,
                    placement: 'top',
                    trigger: 'hover',
                    container: 'body'
                });
            }
        });
        
        // Render lịch
        window.calendar.render();
        
        // Tải sự kiện từ server (chỉ gọi một lần sau khi render)
        loadEvents();
        
        // Thêm nút tạo sự kiện mới
        document.getElementById('addEventBtn').addEventListener('click', function() {
            const today = new Date();
            showEventForm(today);
        });
        
    } catch (e) {
        console.error("Lỗi khởi tạo lịch:", e);
    }
}

/**
 * Tải sự kiện từ API
 */
function loadEvents() {
    $.ajax({
        url: '/dashboard/api/events/',
        method: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function(events) {
            if (window.calendar) {
                window.calendar.removeAllEvents();
                events.forEach(event => {
                    window.calendar.addEvent(event);
                });
            }
        },
        error: function(xhr, status, error) {
            console.error("Lỗi khi tải sự kiện:", error);
            console.log("Lỗi API:", xhr.status, error);
        }
    });
}

/**
 * Hiển thị modal sự kiện trong ngày
 */
function showDayEvents(date) {
    const formattedDate = date.toLocaleDateString('vi-VN', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    // Lấy các sự kiện trong ngày này
    const events = window.calendar ? window.calendar.getEvents().filter(event => {
        const eventDate = new Date(event.start);
        return eventDate.toDateString() === date.toDateString();
    }) : [];
    
    // Tạo HTML cho danh sách sự kiện
    let eventsHtml = '';
    
    if (events.length > 0) {
        events.forEach(event => {
            // Định dạng thời gian
            const startTime = event.start ? new Date(event.start).toLocaleTimeString('vi-VN', {hour: '2-digit', minute: '2-digit'}) : '00:00';
            const endTime = event.end ? new Date(event.end).toLocaleTimeString('vi-VN', {hour: '2-digit', minute: '2-digit'}) : '00:00';
            
            // Lấy màu dựa trên loại sự kiện
            const eventColor = event.backgroundColor || getBorderColorForEventType(event.extendedProps?.type || 'other');
            
            eventsHtml += `
                <div class="event-card" style="
                    background: #fff;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                    border-left: 5px solid ${eventColor};
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                " data-event-id="${event.id}">
                    <div class="event-time" style="
                        font-size: 13px;
                        color: #6c757d;
                        margin-bottom: 8px;
                        display: flex;
                        align-items: center;
                    ">
                        <i class="far fa-clock mr-1" style="margin-right: 5px; color: #df2626;"></i> 
                        ${event.allDay ? 'Cả ngày' : `${startTime} - ${endTime}`}
                    </div>
                    <div class="event-title" style="
                        font-weight: 700;
                        margin-bottom: 8px;
                        font-size: 16px;
                        color: #333;
                    ">${event.title}</div>
                    ${event.extendedProps?.description ? `<div class="event-desc" style="
                        font-size: 14px;
                        color: #495057;
                        line-height: 1.4;
                    ">${event.extendedProps.description}</div>` : ''}
                    <div class="event-actions" style="
                        position: absolute;
                        right: 15px;
                        top: 15px;
                        display: flex;
                        gap: 8px;
                    ">
                        <button class="btn btn-sm btn-outline-primary edit-event-btn" title="Sửa sự kiện" style="
                            padding: 4px 8px;
                            font-size: 12px;
                            border-radius: 5px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                            color: #4e73df;
                            border-color: #4e73df;
                        ">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-event-btn" title="Xóa sự kiện" style="
                            padding: 4px 8px;
                            font-size: 12px;
                            border-radius: 5px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                            color: #e74a3b;
                            border-color: #e74a3b;
                        ">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            `;
        });
    } else {
        eventsHtml = '<div class="text-center py-4 text-muted animate__animated animate__fadeIn">Không có sự kiện nào</div>';
    }
    
    // Thêm CSS cho modal
    const modalCSS = `
        <style>
            .day-events-container {
                max-height: 65vh;
                overflow-y: auto;
                padding: 0 5px;
            }
            
            .day-events-container::-webkit-scrollbar {
                width: 6px;
            }
            
            .day-events-container::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 10px;
            }
            
            .day-events-container::-webkit-scrollbar-thumb {
                background: #c1c1c1;
                border-radius: 10px;
            }
            
            #createNewEventBtn {
                background-color: #df2626;
                border-color: #df2626;
                padding: 10px 20px;
                font-weight: 600;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(223, 38, 38, 0.3);
                transition: all 0.3s ease;
            }
            
            #createNewEventBtn:hover {
                background-color: #c51f1f;
                border-color: #c51f1f;
                transform: translateY(-2px);
                box-shadow: 0 6px 15px rgba(223, 38, 38, 0.4);
            }
            
            .event-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            }
            
            .event-card:hover .event-actions {
                opacity: 1;
                visibility: visible;
            }
        </style>
    `;
    
    // Hiển thị modal với SweetAlert2
    Swal.fire({
        title: `<i class="far fa-calendar-alt mr-2"></i>Sự kiện ngày ${formattedDate}`,
        html: `
            ${modalCSS}
            <div class="day-events-container">
                <div class="day-events-list">
                    ${eventsHtml}
                </div>
                <div class="text-center mt-4">
                    <button id="createNewEventBtn" class="btn btn-primary btn-lg">
                        <i class="fas fa-plus mr-2"></i> Tạo sự kiện mới
                    </button>
                </div>
            </div>
        `,
        showCloseButton: true,
        showConfirmButton: false,
        width: '500px',
        customClass: {
            container: 'day-events-modal-container',
            popup: 'animate__animated animate__fadeInDown',
            title: 'day-events-title',
            content: 'day-events-content'
        },
        didOpen: () => {
            // Thêm animation cho nút
            const createBtn = document.getElementById('createNewEventBtn');
            if (createBtn) {
                createBtn.classList.add('pulse-animation');
            }
            
            // Thêm event listener cho nút "Tạo sự kiện mới"
            document.getElementById('createNewEventBtn').addEventListener('click', () => {
                Swal.close();
                setTimeout(() => {
                    showEventForm(date);
                }, 300);
            });
            
            // Thêm event listener cho các nút sửa và xóa
            document.querySelectorAll('.edit-event-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const eventCard = e.target.closest('.event-card');
                    const eventId = eventCard.getAttribute('data-event-id');
                    const event = window.calendar.getEventById(eventId);
                    
                    if (event) {
                        Swal.close();
                        setTimeout(() => {
                            editEvent(event);
                        }, 300);
                    }
                });
            });
            
            document.querySelectorAll('.delete-event-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const eventCard = e.target.closest('.event-card');
                    const eventId = eventCard.getAttribute('data-event-id');
                    const event = window.calendar.getEventById(eventId);
                    
                    if (event) {
                        Swal.close();
                        setTimeout(() => {
                            deleteEvent(event);
                        }, 300);
                    }
                });
            });
        }
    });
}

/**
 * Hiển thị form tạo/sửa sự kiện
 */
function showEventForm(date, event = null) {
    const isEdit = event !== null;
    const formattedDate = date.toLocaleDateString('vi-VN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    // Lấy giá trị mặc định cho form từ sự kiện nếu đang chỉnh sửa
    const defaultTitle = isEdit ? event.title : '';
    const defaultType = isEdit ? event.extendedProps.type : 'other';
    const defaultDesc = isEdit ? event.extendedProps.description : '';
    const defaultAllDay = isEdit ? event.allDay : false;
    
    // Định dạng ngày và giờ cho input
    const defaultDate = formatDateForInput(date);
    const defaultStartTime = isEdit && !event.allDay ? formatTimeForInput(event.start) : '09:00';
    const defaultEndTime = isEdit && !event.allDay && event.end ? formatTimeForInput(event.end) : '10:00';
    
    Swal.fire({
        title: isEdit ? 'Chỉnh sửa sự kiện' : 'Tạo sự kiện mới',
        html: `
            <form id="eventForm" class="event-form">
                <div class="form-group">
                    <label for="eventTitle">Tiêu đề</label>
                    <input type="text" class="form-control" id="eventTitle" value="${defaultTitle}" required>
                </div>
                <div class="form-group">
                    <label for="eventType">Loại sự kiện</label>
                    <select class="form-control" id="eventType">
                        <option value="meeting" ${defaultType === 'meeting' ? 'selected' : ''}>Cuộc họp</option>
                        <option value="deadline" ${defaultType === 'deadline' ? 'selected' : ''}>Deadline</option>
                        <option value="reminder" ${defaultType === 'reminder' ? 'selected' : ''}>Nhắc nhở</option>
                        <option value="other" ${defaultType === 'other' ? 'selected' : ''}>Khác</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="eventDate">Ngày</label>
                    <input type="date" class="form-control" id="eventDate" value="${defaultDate}" required>
                </div>
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="eventAllDay" ${defaultAllDay ? 'checked' : ''}>
                    <label class="form-check-label" for="eventAllDay">
                        Cả ngày
                    </label>
                </div>
                <div id="timeFields" class="${defaultAllDay ? 'd-none' : ''}">
                    <div class="row">
                        <div class="col-6">
                            <div class="form-group">
                                <label for="eventStartTime">Thời gian bắt đầu</label>
                                <input type="time" class="form-control" id="eventStartTime" value="${defaultStartTime}">
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="form-group">
                                <label for="eventEndTime">Thời gian kết thúc</label>
                                <input type="time" class="form-control" id="eventEndTime" value="${defaultEndTime}">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="eventDescription">Mô tả</label>
                    <textarea class="form-control" id="eventDescription" rows="3">${defaultDesc}</textarea>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: isEdit ? 'Cập nhật' : 'Tạo',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#df2626',
        cancelButtonColor: '#6c757d',
        width: '500px',
        customClass: {
            popup: 'animate__animated animate__fadeInDown'
        },
        didOpen: () => {
            // Toggle hiển thị trường thời gian khi checkbox "Cả ngày" thay đổi
            document.getElementById('eventAllDay').addEventListener('change', function() {
                const timeFields = document.getElementById('timeFields');
                if (this.checked) {
                    timeFields.classList.add('d-none');
                } else {
                    timeFields.classList.remove('d-none');
                }
            });
        },
        preConfirm: () => {
            const title = document.getElementById('eventTitle').value;
            if (!title) {
                Swal.showValidationMessage('Vui lòng nhập tiêu đề sự kiện');
                return false;
            }
            
            const eventType = document.getElementById('eventType').value;
            const eventDate = document.getElementById('eventDate').value;
            const eventAllDay = document.getElementById('eventAllDay').checked;
            const eventStartTime = document.getElementById('eventStartTime').value;
            const eventEndTime = document.getElementById('eventEndTime').value;
            const eventDescription = document.getElementById('eventDescription').value;
            
            // Tạo đối tượng Date từ các giá trị đầu vào
            let startDate = new Date(eventDate);
            let endDate = new Date(eventDate);
            
            if (!eventAllDay) {
                const [startHours, startMinutes] = eventStartTime.split(':');
                const [endHours, endMinutes] = eventEndTime.split(':');
                
                startDate.setHours(parseInt(startHours), parseInt(startMinutes), 0);
                endDate.setHours(parseInt(endHours), parseInt(endMinutes), 0);
                
                // Kiểm tra nếu thời gian kết thúc trước thời gian bắt đầu
                if (endDate < startDate) {
                    Swal.showValidationMessage('Thời gian kết thúc phải sau thời gian bắt đầu');
                    return false;
                }
            }
            
            return {
                title: title,
                type: eventType,
                start: startDate,
                end: eventAllDay ? null : endDate,
                allDay: eventAllDay,
                description: eventDescription,
                id: isEdit ? event.id : null
            };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const eventData = result.value;
            
            if (isEdit) {
                // Cập nhật sự kiện
                updateEvent(eventData);
            } else {
                // Tạo sự kiện mới
                createEvent(eventData);
            }
        }
    });
}

/**
 * Tạo sự kiện mới
 */
function createEvent(eventData) {
    $.ajax({
        url: '/dashboard/api/events/create/',
        method: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: JSON.stringify({
            title: eventData.title,
            type: eventData.type,
            start: eventData.start.toISOString(),
            end: eventData.end ? eventData.end.toISOString() : null,
            allDay: eventData.allDay,
            description: eventData.description
        }),
        success: function(response) {
            // Thêm sự kiện vào lịch
            const color = getEventColor(eventData.type);
            window.calendar.addEvent({
                id: response.id,
                title: eventData.title,
                start: eventData.start,
                end: eventData.end,
                allDay: eventData.allDay,
                backgroundColor: color,
                borderColor: color,
                extendedProps: {
                    type: eventData.type,
                    description: eventData.description
                }
            });
            
            Swal.fire({
                title: 'Thành công!',
                text: 'Sự kiện đã được tạo thành công.',
                icon: 'success',
                confirmButtonColor: '#df2626',
                showClass: {
                    popup: 'animate__animated animate__fadeIn'
                },
                hideClass: {
                    popup: 'animate__animated animate__fadeOut'
                }
            });
        },
        error: function(xhr, status, error) {
            console.error("Lỗi khi tạo sự kiện:", error);
            Swal.fire({
                title: 'Lỗi!',
                text: 'Không thể tạo sự kiện. Vui lòng thử lại.',
                icon: 'error',
                confirmButtonColor: '#df2626'
            });
        }
    });
}

/**
 * Chỉnh sửa sự kiện
 */
function editEvent(event) {
    showEventForm(event.start, event);
}

/**
 * Xóa sự kiện
 */
function deleteEvent(event) {
    Swal.fire({
        title: 'Xác nhận xóa?',
        text: `Bạn có chắc chắn muốn xóa sự kiện "${event.title}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#df2626',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Xóa',
        cancelButtonText: 'Hủy',
        showClass: {
            popup: 'animate__animated animate__fadeIn'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: `/dashboard/api/events/${event.id}/delete/`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function(response) {
                    event.remove();
                    Swal.fire({
                        title: 'Đã xóa!',
                        text: 'Sự kiện đã được xóa thành công.',
                        icon: 'success',
                        confirmButtonColor: '#df2626',
                        showClass: {
                            popup: 'animate__animated animate__fadeIn'
                        },
                        hideClass: {
                            popup: 'animate__animated animate__fadeOut'
                        }
                    });
                },
                error: function(xhr, status, error) {
                    console.error("Lỗi khi xóa sự kiện:", error);
                    Swal.fire({
                        title: 'Lỗi!',
                        text: 'Không thể xóa sự kiện. Vui lòng thử lại.',
                        icon: 'error',
                        confirmButtonColor: '#df2626'
                    });
                }
            });
        }
    });
}

/**
 * Format date cho input date
 */
function formatDateForInput(date) {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

/**
 * Format time cho input time
 */
function formatTimeForInput(date) {
    const d = new Date(date);
    let hours = '' + d.getHours();
    let minutes = '' + d.getMinutes();

    if (hours.length < 2) 
        hours = '0' + hours;
    if (minutes.length < 2) 
        minutes = '0' + minutes;

    return [hours, minutes].join(':');
}

/**
 * Lấy màu cho sự kiện
 */
function getEventColor(eventType) {
    const colors = {
        meeting: '#4e73df',
        deadline: '#e74a3b',
        reminder: '#f6c23e',
        other: '#1cc88a'
    };
    return colors[eventType] || '#4e73df';
}

/**
 * Lấy màu viền cho loại sự kiện
 */
function getBorderColorForEventType(type) {
    const colors = {
        'meeting': '#4e73df',
        'deadline': '#e74a3b', 
        'reminder': '#f6c23e',
        'other': '#1cc88a'
    };
    return colors[type] || '#4e73df';
}

/**
 * Kiểm tra trạng thái đồng bộ với Google Calendar
 */
function checkSyncStatus() {
    fetch('/dashboard/api/calendar/google-status/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const syncBtn = document.getElementById('syncGoogleBtn');
        if (!syncBtn) return;
        
        if (data.is_synced) {
            syncBtn.innerHTML = '<i class="fas fa-check-circle"></i> Đã đồng bộ với Google';
            syncBtn.classList.add('btn-success');
            syncBtn.classList.remove('btn-sync-google');
        } else {
            syncBtn.innerHTML = '<i class="fab fa-google"></i> Đồng bộ với Google Calendar';
        }
    })
    .catch(error => {
        console.error('Lỗi kiểm tra trạng thái đồng bộ:', error);
    });
}

/**
 * Cập nhật thống kê dashboard
 */
function updateDashboardStats() {
    // Giả lập việc lấy dữ liệu từ API
    const statsData = {
        revenue: {
            value: 125000000,
            change: 15.7,
            period: 'tháng'
        },
        orders: {
            value: 458,
            change: 8.3,
            period: 'tháng'
        },
        customers: {
            value: 289,
            change: 3.5,
            period: 'tháng'
        },
        subscriptions: {
            value: 145,
            change: -2.1,
            period: 'tháng'
        }
    };
    
    // Cập nhật từng thẻ thống kê
    Object.keys(statsData).forEach(key => {
        updateStatCard(`${key}Stats`, statsData[key].value, statsData[key].change);
    });
}

/**
 * Cập nhật thông tin thẻ thống kê
 */
function updateStatCard(elementId, value, change) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Định dạng giá trị theo loại dữ liệu
    let formattedValue;
    if (elementId === 'revenueStats') {
        formattedValue = new Intl.NumberFormat('vi-VN', { 
            style: 'currency', 
            currency: 'VND',
            maximumFractionDigits: 0 
        }).format(value);
    } else {
        formattedValue = new Intl.NumberFormat('vi-VN').format(value);
    }
    
    // Cập nhật giá trị
    const valueElement = element.querySelector('.stat-value');
    if (valueElement) valueElement.textContent = formattedValue;
    
    // Cập nhật % thay đổi
    const changeElement = element.querySelector('.stat-change');
    if (changeElement) {
        const changeAbs = Math.abs(change).toFixed(1);
        const icon = change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        const color = change >= 0 ? 'text-success' : 'text-danger';
        
        changeElement.innerHTML = `<i class="fas ${icon} mr-1"></i> ${changeAbs}%`;
        changeElement.className = `stat-change ${color}`;
    }
}

/**
 * Xử lý các tham số URL
 */
function handleUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Xử lý thông báo thành công
    if (urlParams.has('success')) {
        const message = urlParams.get('message') || 'Thao tác đã hoàn thành thành công!';
    Swal.fire({
            title: 'Thành công!',
            text: message,
            icon: 'success',
        confirmButtonColor: '#df2626',
            timer: 3000,
            timerProgressBar: true
        });
    }
    
    // Xử lý thông báo lỗi
    if (urlParams.has('error')) {
        const message = urlParams.get('message') || 'Đã xảy ra lỗi khi thực hiện thao tác!';
        Swal.fire({
            title: 'Lỗi!',
            text: message,
            icon: 'error',
            confirmButtonColor: '#df2626'
        });
    }
    
    // Xử lý các tham số khác
    if (urlParams.has('view')) {
        const view = urlParams.get('view');
        // Chuyển tab hoặc hiển thị nội dung theo yêu cầu
        if (view === 'calendar') {
            // Cuộn đến lịch
            const calendarElement = document.getElementById('calendar');
            if (calendarElement) {
                calendarElement.scrollIntoView({ behavior: 'smooth' });
            }
        } else if (view === 'revenue') {
            // Cuộn đến biểu đồ doanh thu
            const revenueElement = document.getElementById('revenueChart');
            if (revenueElement) {
                revenueElement.scrollIntoView({ behavior: 'smooth' });
            }
        }
    }
    
    // Xóa các tham số URL để tránh lặp lại thông báo khi làm mới trang
    if (urlParams.has('success') || urlParams.has('error') || urlParams.has('message')) {
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }
}

/**
 * Thiết lập các sự kiện
 */
function setupEventListeners() {
    // Thêm sự kiện xử lý cho nút làm mới dữ liệu
    const refreshButton = document.getElementById('refreshDashboardBtn');
    if (refreshButton) {
        refreshButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Hiệu ứng xoay biểu tượng
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.add('fa-spin');
            }
            
            // Làm mới dữ liệu
            refreshDashboardData();
            
            // Sau 1 giây, dừng hiệu ứng xoay
            setTimeout(() => {
                if (icon) {
                    icon.classList.remove('fa-spin');
                }
            }, 1000);
        });
    }
    
    // Thêm sự kiện xử lý cho nút xuất báo cáo
    const exportButtons = document.querySelectorAll('.export-report-btn');
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const reportType = this.getAttribute('data-report');
            
            if (reportType === 'revenue') {
                exportRevenueReport();
            } else if (reportType === 'profit') {
                exportProfitReport();
            }
        });
    });
    
    // Xử lý nút thêm sự kiện mới
    const addEventButton = document.getElementById('addEventBtn');
    if (addEventButton) {
        addEventButton.addEventListener('click', function(e) {
            e.preventDefault();
            const today = new Date().toISOString().slice(0, 10);
            showAddEventModal(today, today);
        });
    }
    
    // Xử lý nút hướng dẫn
    const tutorialButton = document.getElementById('showTutorialBtn');
    if (tutorialButton) {
        tutorialButton.addEventListener('click', function(e) {
            e.preventDefault();
            showDashboardTutorial();
        });
    }
    
    // Xử lý các nút lọc biểu đồ
    const chartFilterButtons = document.querySelectorAll('.chart-filter');
    chartFilterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const chartId = this.getAttribute('data-chart');
            const timeRange = this.getAttribute('data-range');
            
            // Cập nhật UI
            const filterContainer = this.closest('.dropdown-menu');
            if (filterContainer) {
                filterContainer.querySelectorAll('.dropdown-item').forEach(item => {
                    item.classList.remove('active');
                });
                this.classList.add('active');
                
                const filterText = this.textContent.trim();
                const dropdownButton = filterContainer.previousElementSibling;
                if (dropdownButton && dropdownButton.querySelector('.filter-text')) {
                    dropdownButton.querySelector('.filter-text').textContent = filterText;
                }
            }
            
            // Cập nhật biểu đồ
            updateChart(chartId, timeRange);
        });
    });
}

/**
 * Khởi tạo tất cả các thành phần khi trang đã tải xong
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Trang đã tải xong, bắt đầu khởi tạo các thành phần...");
    
    try {
        // Khởi tạo lịch
        setTimeout(() => {
            initCalendar();
        }, 0);
        
        // Khởi tạo các biểu đồ
        setTimeout(() => {
            initRevenueChart();
            
            setTimeout(() => {
                initProfitChart();
                initOrderStatusChart();
            }, 100);
        }, 200);
        
        // Kiểm tra trạng thái đồng bộ
        setTimeout(() => {
            checkSyncStatus();
        }, 300);
        
        // Khởi tạo các thành phần khác
        setTimeout(() => {
            updateDashboardStats();
            setupEventListeners();
        }, 400);
        
        // Kiểm tra tham số URL
        handleUrlParameters();
        
    } catch (error) {
        console.error("Lỗi khi khởi tạo dashboard:", error);
    Swal.fire({
            icon: 'error',
            title: 'Đã xảy ra lỗi',
            text: 'Có lỗi khi tải dashboard. Vui lòng tải lại trang.',
            confirmButtonColor: '#df2626',
            confirmButtonText: 'Tải lại trang',
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.reload();
            }
        });
    }
});

/**
 * Xuất báo cáo doanh thu
 */
function exportRevenueReport() {
    Swal.fire({
        title: 'Xuất báo cáo doanh thu',
        html: `
            <form id="exportRevenueForm">
                <div class="mb-3">
                    <label class="form-label">Khoảng thời gian</label>
                    <select class="form-control" id="reportTimeRange">
                        <option value="day">Ngày</option>
                        <option value="week">Tuần</option>
                        <option value="month" selected>Tháng</option>
                        <option value="quarter">Quý</option>
                        <option value="year">Năm</option>
                    </select>
            </div>
                <div class="mb-3">
                    <label class="form-label">Định dạng</label>
                    <select class="form-control" id="reportFormat">
                        <option value="pdf">PDF</option>
                        <option value="excel">Excel</option>
                        <option value="csv">CSV</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Chi tiết báo cáo</label>
                    <select class="form-control" id="reportDetail">
                        <option value="summary">Tóm tắt</option>
                        <option value="detailed">Chi tiết</option>
                        <option value="full">Đầy đủ</option>
                    </select>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Xuất báo cáo',
                cancelButtonText: 'Hủy',
        confirmButtonColor: '#df2626'
            }).then((result) => {
                if (result.isConfirmed) {
            const timeRange = document.getElementById('reportTimeRange').value;
            const format = document.getElementById('reportFormat').value;
            const detail = document.getElementById('reportDetail').value;
            
            // Xác định phạm vi thời gian
            let dateRange;
            if (timeRange === 'day') {
                dateRange = new Date().toLocaleDateString('vi-VN');
            } else if (timeRange === 'week') {
                dateRange = 'tuần ' + getWeekNumber(new Date());
            } else if (timeRange === 'month') {
                dateRange = 'tháng ' + (new Date().getMonth() + 1) + '/' + new Date().getFullYear();
            } else if (timeRange === 'quarter') {
                const quarter = Math.floor(new Date().getMonth() / 3) + 1;
                dateRange = 'quý ' + quarter + '/' + new Date().getFullYear();
            } else {
                dateRange = 'năm ' + new Date().getFullYear();
            }
            
            // Giả lập xuất báo cáo
                    Swal.fire({
                title: 'Đang chuẩn bị báo cáo...',
                html: 'Vui lòng đợi trong giây lát',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                    
                    // Giả lập tạo báo cáo
                    setTimeout(() => {
                        Swal.fire({
                        icon: 'success',
                            title: 'Đã tạo báo cáo',
                            html: `Báo cáo doanh thu ${dateRange} (${detail === 'summary' ? 'tóm tắt' : detail === 'detailed' ? 'chi tiết' : 'đầy đủ'}) đã được tạo thành công.<br><br>
                                <a href="#" class="btn btn-sm btn-primary download-link">
                                    <i class="fas fa-download"></i> Tải báo cáo ${format.toUpperCase()}
                                </a>`,
                        confirmButtonColor: '#df2626'
                    });
                    }, 2000);
                }
            });
        }
    });
}

/**
 * Xuất báo cáo lợi nhuận
 */
function exportProfitReport() {
    // Tương tự như exportRevenueReport nhưng cho báo cáo lợi nhuận
    Swal.fire({
        title: 'Xuất báo cáo lợi nhuận',
        html: `
            <form id="exportProfitForm">
                <div class="mb-3">
                    <label class="form-label">Khoảng thời gian</label>
                    <select class="form-control" id="profitTimeRange">
                        <option value="day">Ngày</option>
                        <option value="week">Tuần</option>
                        <option value="month" selected>Tháng</option>
                        <option value="quarter">Quý</option>
                        <option value="year">Năm</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Định dạng</label>
                    <select class="form-control" id="profitFormat">
                        <option value="pdf">PDF</option>
                        <option value="excel">Excel</option>
                        <option value="csv">CSV</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Chi tiết báo cáo</label>
                    <select class="form-control" id="profitDetail">
                        <option value="summary">Tóm tắt</option>
                        <option value="detailed">Chi tiết</option>
                        <option value="full">Đầy đủ</option>
                    </select>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: 'Xuất báo cáo',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#df2626'
    }).then((result) => {
        if (result.isConfirmed) {
            const timeRange = document.getElementById('profitTimeRange').value;
            const format = document.getElementById('profitFormat').value;
            const detail = document.getElementById('profitDetail').value;
            
            // Xác định phạm vi thời gian
            let dateRange;
            if (timeRange === 'day') {
                dateRange = new Date().toLocaleDateString('vi-VN');
            } else if (timeRange === 'week') {
                dateRange = 'tuần ' + getWeekNumber(new Date());
            } else if (timeRange === 'month') {
                dateRange = 'tháng ' + (new Date().getMonth() + 1) + '/' + new Date().getFullYear();
            } else if (timeRange === 'quarter') {
                const quarter = Math.floor(new Date().getMonth() / 3) + 1;
                dateRange = 'quý ' + quarter + '/' + new Date().getFullYear();
            } else {
                dateRange = 'năm ' + new Date().getFullYear();
            }
            
            // Giả lập xuất báo cáo
            Swal.fire({
                title: 'Đang chuẩn bị báo cáo...',
                html: 'Vui lòng đợi trong giây lát',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                    
                    // Giả lập tạo báo cáo
                    setTimeout(() => {
                        Swal.fire({
                icon: 'success',
                            title: 'Đã tạo báo cáo',
                            html: `Báo cáo lợi nhuận ${dateRange} (${detail === 'summary' ? 'tóm tắt' : detail === 'detailed' ? 'chi tiết' : 'đầy đủ'}) đã được tạo thành công.<br><br>
                                <a href="#" class="btn btn-sm btn-primary download-link">
                                    <i class="fas fa-download"></i> Tải báo cáo ${format.toUpperCase()}
                                </a>`,
                confirmButtonColor: '#df2626'
                        });
                    }, 2000);
                }
            });
        }
    });
}

/**
 * Hiển thị hướng dẫn sử dụng dashboard
 */
function showDashboardTutorial() {
    const steps = [
        {
            title: 'Tổng quan',
            text: 'Đây là nơi bạn có thể theo dõi các chỉ số kinh doanh quan trọng',
            element: '.stats-row',
            position: 'bottom'
        },
        {
            title: 'Lịch',
            text: 'Quản lý lịch sự kiện và nhắc nhở tại đây',
            element: '#calendar',
            position: 'top'
        },
        {
            title: 'Biểu đồ doanh thu',
            text: 'Theo dõi doanh thu theo thời gian',
            element: '#revenueChart',
            position: 'left'
        },
        {
            title: 'Xuất báo cáo',
            text: 'Bạn có thể xuất báo cáo bất kỳ lúc nào',
            element: '#exportRevenueBtn',
            position: 'right'
        }
    ];
    
    let currentStep = 0;
    
    function showStep(step) {
        const element = document.querySelector(step.element);
        if (!element) {
            console.error(`Không tìm thấy phần tử ${step.element}`);
            nextStep();
            return;
        }
        
        // Xóa highlight cũ
        const prevHighlight = document.querySelector('.tutorial-highlight');
        if (prevHighlight) {
            prevHighlight.classList.remove('tutorial-highlight');
        }
        
        // Thêm highlight mới
        element.classList.add('tutorial-highlight');
        
        // Hiển thị thông tin bước
        Swal.fire({
            title: step.title,
            text: step.text,
            icon: 'info',
            showCancelButton: true,
            confirmButtonText: currentStep < steps.length - 1 ? 'Tiếp tục' : 'Kết thúc',
            cancelButtonText: 'Bỏ qua',
            confirmButtonColor: '#df2626',
            customClass: {
                container: 'tutorial-swal-container',
                popup: `tutorial-popup-${step.position}`
            }
        }).then((result) => {
            // Xóa highlight
            element.classList.remove('tutorial-highlight');
            
            if (result.isConfirmed) {
                nextStep();
        } else {
                // Người dùng bỏ qua tour
                Swal.fire({
                    title: 'Hướng dẫn đã kết thúc',
                    text: 'Bạn có thể mở lại hướng dẫn bất kỳ lúc nào từ menu trợ giúp',
                    icon: 'success',
                    confirmButtonColor: '#df2626',
                    timer: 2000,
                    timerProgressBar: true
                });
            }
        });
    }
    
    function nextStep() {
        currentStep++;
        if (currentStep < steps.length) {
            showStep(steps[currentStep]);
    } else {
            // Kết thúc tour
            Swal.fire({
                title: 'Hoàn thành!',
                text: 'Bạn đã hoàn thành tour hướng dẫn. Chúc bạn sử dụng hiệu quả!',
                icon: 'success',
                confirmButtonColor: '#df2626'
            });
        }
    }
    
    // Bắt đầu tour với bước đầu tiên
    showStep(steps[0]);
}

// Thêm hàm xử lý hiển thị chi tiết đơn hàng
function showOrderDetails(orderId) {
    // Giả lập dữ liệu đơn hàng
    const orderData = {
        id: orderId,
        customer: 'Nguyễn Văn A',
        phone: '0987654321',
        email: 'nguyenvana@email.com',
        products: [
            { name: 'Sản phẩm 1', quantity: 2, price: 500000 },
            { name: 'Sản phẩm 2', quantity: 1, price: 200000 }
        ],
        total: 1200000,
        status: 'Hoàn thành',
        date: '2024-03-08 15:30:00',
        address: '123 Đường ABC, Quận XYZ, TP.HCM'
    };

    Swal.fire({
        title: `<div class="order-title">Chi tiết đơn hàng #${orderId}</div>`,
        html: `
            <div class="order-details">
                <div class="order-section customer-info">
                    <div class="section-header">
                        <i class="fas fa-user-circle"></i>
                        <h6>Thông tin khách hàng</h6>
                    </div>
                    <div class="section-content">
                        <div class="info-row">
                            <span class="info-label"><i class="fas fa-user"></i> Tên:</span>
                            <span class="info-value">${orderData.customer}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label"><i class="fas fa-phone"></i> SĐT:</span>
                            <span class="info-value">${orderData.phone}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label"><i class="fas fa-envelope"></i> Email:</span>
                            <span class="info-value">${orderData.email}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label"><i class="fas fa-map-marker-alt"></i> Địa chỉ:</span>
                            <span class="info-value">${orderData.address}</span>
                        </div>
                    </div>
                </div>

                <div class="order-section order-info">
                    <div class="section-header">
                        <i class="fas fa-info-circle"></i>
                        <h6>Thông tin đơn hàng</h6>
                    </div>
                    <div class="section-content">
                        <div class="info-row">
                            <span class="info-label"><i class="fas fa-calendar"></i> Ngày đặt:</span>
                            <span class="info-value">${orderData.date}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label"><i class="fas fa-check-circle"></i> Trạng thái:</span>
                            <span class="info-value">
                                <span class="badge badge-success">${orderData.status}</span>
                            </span>
                        </div>
                    </div>
                </div>

                <div class="order-section products-info">
                    <div class="section-header">
                        <i class="fas fa-shopping-cart"></i>
                        <h6>Sản phẩm</h6>
                    </div>
                    <div class="section-content">
                        <table class="table table-hover">
                            <thead class="thead-light">
                                <tr>
                                    <th>Sản phẩm</th>
                                    <th class="text-center">SL</th>
                                    <th class="text-right">Đơn giá</th>
                                    <th class="text-right">Thành tiền</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${orderData.products.map(p => `
                                    <tr>
                                        <td>${p.name}</td>
                                        <td class="text-center">${p.quantity}</td>
                                        <td class="text-right">${p.price.toLocaleString('vi-VN')}đ</td>
                                        <td class="text-right">${(p.quantity * p.price).toLocaleString('vi-VN')}đ</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                            <tfoot>
                                <tr class="font-weight-bold">
                                    <td colspan="3" class="text-right">Tổng cộng:</td>
                                    <td class="text-right">${orderData.total.toLocaleString('vi-VN')}đ</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            </div>
        `,
        width: '700px',
        confirmButtonText: 'Đóng',
        confirmButtonColor: '#df2626',
        customClass: {
            container: 'order-details-modal',
            popup: 'order-details-popup',
            content: 'order-details-content'
        }
    });
}

// Thêm event listener cho nút xem chi tiết
document.querySelectorAll('.btn-view-order').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const orderId = this.getAttribute('data-order-id');
        showOrderDetails(orderId);
    });
});

/**
 * Xử lý thay đổi sự kiện (kéo thả hoặc resize)
 */
function handleEventChange(info, action) {
    Swal.fire({
        title: 'Xác nhận thay đổi',
        text: `${action} "${info.event.title}" đến ${info.event.start.toLocaleDateString('vi-VN')}?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#df2626',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Đồng ý',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (!result.isConfirmed) {
            info.revert();
        }
    });
}

/**
 * Tạo nội dung tooltip cho sự kiện
 */
function getEventTooltipContent(event) {
    return `
        <div class="event-tooltip">
            <div class="event-title">${event.title}</div>
            <div class="event-time">
                ${event.allDay ? 'Cả ngày' : `${event.start.toLocaleTimeString('vi-VN')} - ${event.end ? event.end.toLocaleTimeString('vi-VN') : ''}`}
            </div>
            ${event.extendedProps.description ? `<div class="event-desc">${event.extendedProps.description}</div>` : ''}
        </div>
    `;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Khởi tạo biểu đồ doanh thu
 */
function initRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    // Dữ liệu mặc định (tháng)
    const labels = sampleData.revenue.month.labels;
    const data = sampleData.revenue.month.data;
    
    window.dashboardCharts.revenue = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu',
                data: data,
                borderColor: '#df2626',
                backgroundColor: 'rgba(223, 38, 38, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#df2626',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('vi-VN') + 'đ';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toLocaleString('vi-VN') + 'đ';
                        }
                    }
                }
            }
        }
    });
    
    console.log("Biểu đồ doanh thu đã được khởi tạo");
}

/**
 * Khởi tạo biểu đồ lợi nhuận
 */
function initProfitChart() {
    const ctx = document.getElementById('profitChart');
    if (!ctx) return;
    
    // Dữ liệu mặc định (tháng)
    const labels = sampleData.revenue.month.labels;
    const profitData = sampleData.profit.month.profit;
    const costData = sampleData.profit.month.cost;
    
    window.dashboardCharts.profit = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Lợi nhuận',
                    data: profitData,
                    backgroundColor: 'rgba(28, 200, 138, 0.8)',
                    borderColor: '#1cc88a',
                    borderWidth: 1,
                    borderRadius: 5,
                    barThickness: 15
                },
                {
                    label: 'Chi phí',
                    data: costData,
                    backgroundColor: 'rgba(246, 194, 62, 0.8)',
                    borderColor: '#f6c23e',
                    borderWidth: 1,
                    borderRadius: 5,
                    barThickness: 15
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('vi-VN') + 'đ';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toLocaleString('vi-VN') + 'đ';
                        }
                    }
                }
            }
        }
    });
    
    console.log("Biểu đồ lợi nhuận đã được khởi tạo");
}

/**
 * Khởi tạo biểu đồ trạng thái đơn hàng
 */
function initOrderStatusChart() {
    const ctx = document.getElementById('orderStatusChart');
    if (!ctx) return;
    
    // Dữ liệu mặc định (tháng)
    const data = sampleData.order.month;
    
    window.dashboardCharts.order = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: data.colors,
                hoverBackgroundColor: data.hoverColors,
                borderWidth: 1,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    console.log("Biểu đồ trạng thái đơn hàng đã được khởi tạo");
}

/**
 * Cập nhật dữ liệu biểu đồ
 */
function updateChart(chartType, range) {
    if (!window.dashboardCharts[chartType]) return;
    
    // Lấy dữ liệu tương ứng
    const data = sampleData[chartType][range];
    
    if (chartType === 'revenue') {
        // Cập nhật biểu đồ doanh thu
        window.dashboardCharts.revenue.data.labels = data.labels;
        window.dashboardCharts.revenue.data.datasets[0].data = data.data;
        window.dashboardCharts.revenue.update();
    } else if (chartType === 'profit') {
        // Cập nhật biểu đồ lợi nhuận
        window.dashboardCharts.profit.data.labels = sampleData.revenue[range].labels;
        window.dashboardCharts.profit.data.datasets[0].data = data.profit;
        window.dashboardCharts.profit.data.datasets[1].data = data.cost;
        window.dashboardCharts.profit.update();
    } else if (chartType === 'order') {
        // Cập nhật biểu đồ trạng thái đơn hàng
        window.dashboardCharts.order.data.labels = data.labels;
        window.dashboardCharts.order.data.datasets[0].data = data.data;
        window.dashboardCharts.order.data.datasets[0].backgroundColor = data.colors;
        window.dashboardCharts.order.data.datasets[0].hoverBackgroundColor = data.hoverColors;
        window.dashboardCharts.order.update();
    }
}