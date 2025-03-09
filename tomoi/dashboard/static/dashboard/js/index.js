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
 * Hoàn toàn mới - Sửa triệt để vấn đề màu sắc sự kiện
 * Gọi hàm này khi load calendar hoặc khi có thay đổi
 */
function forceEventColoring() {
    console.log("Áp dụng màu sắc cho tất cả sự kiện...");
    
    // Xác định các loại sự kiện và màu sắc tương ứng
    const typeColors = {
        'meeting': '#E63946',    // đỏ
        'task': '#1D3557',       // xanh đậm
        'deadline': '#F77F00',   // cam
        'reminder': '#2A9D8F',   // xanh lá
        'appointment': '#457B9D',// xanh dương
        'other': '#6C757D'       // xám
    };
    
    // Áp dụng màu sắc cho tất cả các sự kiện
    document.querySelectorAll('.fc-event, .fc-daygrid-event, .fc-timegrid-event').forEach(el => {
        // Xác định loại sự kiện từ class
        let eventType = 'other';
        
        if (el.classList.contains('fc-event-type-meeting')) eventType = 'meeting';
        else if (el.classList.contains('fc-event-type-task')) eventType = 'task';
        else if (el.classList.contains('fc-event-type-deadline')) eventType = 'deadline';
        else if (el.classList.contains('fc-event-type-reminder')) eventType = 'reminder';
        else if (el.classList.contains('fc-event-type-appointment')) eventType = 'appointment';
        
        // Lấy màu tương ứng
        const color = typeColors[eventType];
        
        // Áp dụng trực tiếp vào element
        el.style.setProperty('background-color', color, 'important');
        el.style.setProperty('border-color', color, 'important');
        el.style.setProperty('color', 'white', 'important');
        
        // Set data attribute để CSS có thể target dễ dàng hơn
        el.setAttribute('data-event-type', eventType);
        
        // Áp dụng cho tất cả các phần tử con
        el.querySelectorAll('*').forEach(child => {
            child.style.setProperty('color', 'white', 'important');
        });
    });
    
    console.log("Đã áp dụng màu sắc xong.");
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
            // Cấu hình ban đầu
            initialView: 'dayGridMonth',
            locale: 'vi',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
            },
            
            // Cấu hình hiển thị sự kiện
            dayMaxEventRows: false,
            dayMaxEvents: false,
            moreLinkClick: 'day',
            
            // Đảm bảo sự kiện nhiều ngày kết nối đúng
            eventDisplay: 'block',
            displayEventTime: true,
            displayEventEnd: true,
            nextDayThreshold: '00:00:00',
            nowIndicator: true,
            
            // Cấu hình hiển thị
            height: 'auto',
            firstDay: 1,
            
            // Các sự kiện click
            dateClick: function(info) {
                showDayEvents(info.date);
            },
            
            eventClick: function(info) {
                info.jsEvent.preventDefault();
                editEvent(info.event);
            },
            
            // Xử lý hiển thị sự kiện
            eventDidMount: function(info) {
                const eventType = info.event.extendedProps.type || 'other';
                const color = getBorderColorForEventType(eventType);
                
                // Force màu sắc cho sự kiện
                info.el.style.setProperty('background-color', color, 'important');
                info.el.style.setProperty('border-color', color, 'important');
                info.el.style.setProperty('color', 'white', 'important');
                
                // Force màu chữ trắng cho tất cả phần tử con
                info.el.querySelectorAll('*').forEach(child => {
                    child.style.setProperty('color', 'white', 'important');
                });
                
                // Thêm class để CSS có thể target
                info.el.classList.add('fc-event-type-' + eventType);
            },
            
            // Thêm datesSet để force lại màu sắc khi view thay đổi
            datesSet: function() {
                setTimeout(() => {
                    document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(el => {
                        const type = el.className.match(/fc-event-type-(\w+)/);
                        if (type && type[1]) {
                            const color = getBorderColorForEventType(type[1]);
                            el.style.setProperty('background-color', color, 'important');
                            el.style.setProperty('border-color', color, 'important');
                            el.style.setProperty('color', 'white', 'important');
                            
                            el.querySelectorAll('*').forEach(child => {
                                child.style.setProperty('color', 'white', 'important');
                            });
                        }
                    });
                }, 100);
            },
            
            // Các cấu hình còn lại giữ nguyên
            buttonText: {
                today: 'Hôm nay',
                month: 'Tháng',
                week: 'Tuần',
                day: 'Ngày',
                list: 'Danh sách'
            }
        });
        
        // Render lịch
        window.calendar.render();
        
        // Tải sự kiện
        loadEvents();
        
        // Thêm nút Add Event
        setTimeout(addFloatingAddButton, 500);
        
        // Thêm event listener toàn cục để đảm bảo hiển thị đúng
        document.addEventListener('DOMContentLoaded', () => {
            addFloatingAddButton();
            setTimeout(forceEventColoring, 500);
        });
        
    } catch (e) {
        console.error("Lỗi khởi tạo lịch:", e);
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
}

/**
 * Tải sự kiện từ server
 */
function loadEvents() {
    fetch('/dashboard/api/events/')
        .then(response => response.json())
        .then(events => {
            // Xóa tất cả sự kiện hiện có
            window.calendar.removeAllEvents();
            
            // Mảng để theo dõi sự kiện đã thêm
            let addedEvents = [];
            
            // Thêm các sự kiện mới
            events.forEach(event => {
                // Xác định loại và màu sắc
                const eventType = event.type || 'other';
                const color = getBorderColorForEventType(eventType);
                
                // Tạo đối tượng sự kiện với thuộc tính màu cứng
                const calEvent = {
                    id: event.id,
                    title: event.title,
                    start: new Date(event.start),
                    end: event.end ? new Date(event.end) : null,
                    allDay: event.allDay,
                    backgroundColor: color,
                    borderColor: color,
                    textColor: '#FFFFFF',
                    classNames: ['fc-event-type-' + eventType],
                    extendedProps: {
                        type: eventType,
                        description: event.description || ''
                    }
                };
                
                // Thêm sự kiện vào calendar
                const addedEvent = window.calendar.addEvent(calEvent);
                addedEvents.push(addedEvent);
                
                // Áp dụng màu sắc cho event element ngay khi có thể
                setTimeout(() => {
                    const eventEl = document.querySelector(`.fc-event[data-event-id="${event.id}"], .fc-daygrid-event[data-event-id="${event.id}"]`);
                    if (eventEl) {
                        applyColorToEvent(eventEl, color);
                    }
                }, 10);
            });
            
            // Render lại calendar để đảm bảo hiển thị đúng
            window.calendar.render();
            
            // Force màu sắc cho tất cả sự kiện sau khi render
            setTimeout(() => {
                forceAllEventColors();
            }, 100);
            
            return addedEvents;
        });
}

// Hàm mới để áp dụng màu sắc cho một phần tử sự kiện
function applyColorToEvent(element, color) {
    if (!element) return;
    
    // Áp dụng màu sắc với inline style (mức ưu tiên cao nhất)
    element.style = `
        background-color: ${color} !important;
        border-color: ${color} !important;
        color: white !important;
    `;
    
    // Áp dụng màu sắc cho tất cả phần tử con
    element.querySelectorAll('*').forEach(child => {
        child.style = `color: white !important;`;
    });
    
    // Thêm data-attribute để có thể xác định lại sau này
    element.setAttribute('data-color-applied', 'true');
    element.setAttribute('data-event-color', color);
}

// Hàm mới để force màu sắc cho tất cả sự kiện
function forceAllEventColors() {
    const events = window.calendar.getEvents();
    
    events.forEach(event => {
        const eventType = event.extendedProps.type || 'other';
        const color = getBorderColorForEventType(eventType);
        const elements = document.querySelectorAll(`.fc-event[data-event-id="${event.id}"], .fc-daygrid-event[data-event-id="${event.id}"]`);
        
        elements.forEach(el => {
            applyColorToEvent(el, color);
        });
    });
    
    // Ngoài ra tìm kiếm tất cả các sự kiện theo class
    document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(el => {
        // Tìm loại từ class
        let eventType = null;
        const classes = el.className.split(' ');
        
        for (const cls of classes) {
            if (cls.includes('fc-event-type-')) {
                eventType = cls.replace('fc-event-type-', '');
                break;
            }
        }
        
        if (eventType) {
            const color = getBorderColorForEventType(eventType);
            applyColorToEvent(el, color);
        }
    });
}

/**
 * Hiển thị danh sách sự kiện trong ngày
 */
function showDayEvents(date) {
    const formattedDate = moment(date).format('DD/MM/YYYY');
    const events = window.calendar.getEvents();
    const dayEvents = events.filter(event => {
        const eventDate = moment(event.start);
        return eventDate.format('DD/MM/YYYY') === formattedDate;
    });
    
    let eventsHtml = '';
    
    if (dayEvents.length > 0) {
        eventsHtml = `<ul class="event-list">`;
        
        dayEvents.forEach(event => {
            const startTime = moment(event.start).format('HH:mm');
            const endTime = event.end ? moment(event.end).format('HH:mm') : '';
            const timeDisplay = event.allDay ? 'Cả ngày' : `${startTime}${endTime ? ' - ' + endTime : ''}`;
            const eventType = event.extendedProps.type || 'other';
            const description = event.extendedProps.description || 'Không có mô tả';
            const typeText = getEventTypeText(eventType);
            const borderColor = getBorderColorForEventType(eventType);
            
            eventsHtml += `
                <li class="event-list-item" data-type="${eventType}" data-id="${event.id}">
                    <div class="event-list-item-title">${event.title}</div>
                    <div class="event-list-item-time"><i class="far fa-clock mr-1"></i> ${timeDisplay}</div>
                    <div class="event-list-item-description">${description}</div>
                    <span class="event-list-item-type" data-type="${eventType}">${typeText}</span>
                    <div class="mt-2 d-flex justify-content-end">
                        <button class="btn btn-sm btn-outline-primary mr-2 edit-event-btn" data-id="${event.id}">
                            <i class="fas fa-edit"></i> Sửa
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-event-btn" data-id="${event.id}">
                            <i class="fas fa-trash-alt"></i> Xóa
                        </button>
                    </div>
                </li>
            `;
        });
        
        eventsHtml += `</ul>`;
    } else {
        eventsHtml = `<div class="alert alert-info">
            <i class="fas fa-info-circle mr-2"></i> Không có sự kiện nào vào ngày ${formattedDate}
        </div>`;
    }
    
    Swal.fire({
        title: `Sự kiện ngày ${formattedDate}`,
        html: eventsHtml,
        width: '600px',
        showCloseButton: true,
        showConfirmButton: false,
        showCancelButton: true,
        cancelButtonText: 'Đóng',
        cancelButtonColor: '#6c757d',
        footer: `<button id="add-event-day-btn" class="btn btn-primary"><i class="fas fa-plus"></i> Thêm sự kiện</button>`,
        didOpen: () => {
            // Thêm sự kiện cho các nút
            document.querySelectorAll('.edit-event-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const eventId = btn.getAttribute('data-id');
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
                    const eventId = btn.getAttribute('data-id');
                    Swal.close();
                    setTimeout(() => {
                        confirmDeleteEvent(eventId);
                    }, 300);
                });
            });
            
            // Thêm sự kiện cho nút thêm mới
            document.getElementById('add-event-day-btn').addEventListener('click', () => {
                Swal.close();
                setTimeout(() => {
                    showCreateEventModal(date);
                }, 300);
            });
        }
    });
}

/**
 * Hiển thị form tạo/chỉnh sửa sự kiện
 */
function showEventForm(date, event = null) {
    // Tạo tiêu đề modal
    const modalTitle = event ? 'Chỉnh sửa sự kiện' : 'Tạo sự kiện mới';
    
    // Chuẩn bị ngày/giờ
    const eventDate = date ? date : (event ? event.start : new Date());
    
    // Format ngày theo định dạng d/m/y cho hiển thị
    const formattedDateDisplay = eventDate.toLocaleDateString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        timeZone: 'Asia/Ho_Chi_Minh'
    });
    
    // Format ngày theo định dạng yyyy-mm-dd cho input date
    const formattedDate = eventDate.toISOString().substring(0, 10);
    
    // Chuẩn bị ngày kết thúc
    let endDate, endDateDisplay;
    if (event && event.end) {
        // Nếu là sự kiện đã có, lấy ngày kết thúc từ sự kiện
        const eventEnd = new Date(event.end);
        if (event.allDay) {
            // Nếu là sự kiện cả ngày, trừ đi 1 ngày vì FullCalendar tính ngày kết thúc là ngày tiếp theo
            eventEnd.setDate(eventEnd.getDate() - 1);
        }
        endDate = eventEnd.toISOString().substring(0, 10);
        endDateDisplay = eventEnd.toLocaleDateString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            timeZone: 'Asia/Ho_Chi_Minh'
        });
    } else {
        // Nếu là sự kiện mới, mặc định ngày kết thúc = ngày bắt đầu
        endDate = formattedDate;
        endDateDisplay = formattedDateDisplay;
    }
    
    // Chuẩn bị giờ bắt đầu
    let startTime = '09:00';
    if (event && event.start) {
        const eventStart = new Date(event.start);
        startTime = eventStart.getHours().toString().padStart(2, '0') + ':' + 
                    eventStart.getMinutes().toString().padStart(2, '0');
    }
    
    // Chuẩn bị giờ kết thúc
    let endTime = '10:00';
    if (event && event.end) {
        const eventEnd = new Date(event.end);
        endTime = eventEnd.getHours().toString().padStart(2, '0') + ':' + 
                 eventEnd.getMinutes().toString().padStart(2, '0');
    }
    
    // Tạo HTML cho form với thiết kế đẹp hơn và thêm trường ngày kết thúc
    Swal.fire({
        title: `<div class="event-form-title"><i class="fas fa-calendar-plus"></i> ${modalTitle}</div>`,
        html: `
            <form id="eventForm" class="text-left event-create-form">
                <div class="form-group mb-3">
                    <label for="swal-event-title" class="form-label">
                        <i class="fas fa-heading text-primary"></i> Tiêu đề <span class="text-danger">*</span>
                    </label>
                    <input type="text" class="form-control form-control-lg" id="swal-event-title" 
                        value="${event ? event.title : ''}" placeholder="Nhập tiêu đề sự kiện" required>
                </div>
                
                <div class="form-group mb-3">
                    <label for="swal-event-type" class="form-label">
                        <i class="fas fa-tag text-info"></i> Loại sự kiện
                    </label>
                    <select class="form-control form-select" id="swal-event-type">
                        <option value="meeting" ${event && event.extendedProps.type === 'meeting' ? 'selected' : ''}>
                            <i class="fas fa-users"></i> Cuộc họp
                        </option>
                        <option value="deadline" ${event && event.extendedProps.type === 'deadline' ? 'selected' : ''}>
                            <i class="fas fa-hourglass-end"></i> Deadline
                        </option>
                        <option value="reminder" ${event && event.extendedProps.type === 'reminder' ? 'selected' : ''}>
                            <i class="fas fa-bell"></i> Nhắc nhở
                        </option>
                        <option value="other" ${!event || event.extendedProps.type === 'other' ? 'selected' : ''}>
                            <i class="fas fa-calendar-day"></i> Khác
                        </option>
                    </select>
                    <div class="event-type-preview mt-2">
                        <span class="badge" style="background-color: ${getBorderColorForEventType(event ? event.extendedProps.type : 'other')}">
                            Xem trước màu sự kiện
                        </span>
                    </div>
                </div>
                
                <div class="form-check mb-3 all-day-check">
                    <input class="form-check-input" type="checkbox" id="swal-all-day-event" ${event && event.allDay ? 'checked' : ''}>
                    <label class="form-check-label" for="swal-all-day-event">
                        <i class="fas fa-clock"></i> Cả ngày
                    </label>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="swal-event-date" class="form-label">
                            <i class="fas fa-calendar-alt text-success"></i> Ngày bắt đầu
                        </label>
                        <div class="input-group date">
                            <input type="date" class="form-control event-date-input" id="swal-event-date" value="${formattedDate}" required>
                            <div class="input-group-text d-none d-md-flex">
                                <i class="fas fa-calendar-alt"></i>
                            </div>
                        </div>
                        <div class="date-display-text form-text text-muted">Hiển thị: ${formattedDateDisplay}</div>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="swal-event-end-date" class="form-label">
                            <i class="fas fa-calendar-check text-danger"></i> Ngày kết thúc
                        </label>
                        <div class="input-group date">
                            <input type="date" class="form-control event-date-input" id="swal-event-end-date" value="${endDate}" required>
                            <div class="input-group-text d-none d-md-flex">
                                <i class="fas fa-calendar-alt"></i>
                            </div>
                        </div>
                        <div class="date-display-text form-text text-muted">Hiển thị: ${endDateDisplay}</div>
                    </div>
                </div>
                
                <div class="row time-inputs ${event && event.allDay ? 'd-none' : ''}">
                    <div class="col-md-6 mb-3">
                        <label for="swal-event-start-time" class="form-label">
                            <i class="fas fa-hourglass-start text-warning"></i> Thời gian bắt đầu
                        </label>
                        <input type="time" class="form-control" id="swal-event-start-time" value="${startTime}">
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="swal-event-end-time" class="form-label">
                            <i class="fas fa-hourglass-end text-danger"></i> Thời gian kết thúc
                        </label>
                        <input type="time" class="form-control" id="swal-event-end-time" value="${endTime}">
                    </div>
                </div>
                
                <div class="form-group mb-3">
                    <label for="swal-event-description" class="form-label">
                        <i class="fas fa-align-left text-secondary"></i> Mô tả
                    </label>
                    <textarea class="form-control" id="swal-event-description" rows="3" 
                        placeholder="Nhập mô tả sự kiện (không bắt buộc)">${event && event.extendedProps.description ? event.extendedProps.description : ''}</textarea>
                </div>
            </form>
        `,
        showCancelButton: true,
        confirmButtonText: event ? 'Cập nhật' : 'Tạo mới',
        cancelButtonText: 'Hủy',
        showDenyButton: event ? true : false,
        denyButtonText: event ? 'Xóa' : '',
        confirmButtonColor: '#df2626',
        denyButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        customClass: {
            confirmButton: 'event-form-confirm',
            denyButton: 'event-form-deny',
            cancelButton: 'event-form-cancel'
        },
        focusConfirm: false,
        didOpen: () => {
            // Xử lý sự kiện khi checkbox "Cả ngày" thay đổi
            document.getElementById('swal-all-day-event').addEventListener('change', function() {
                const timeInputs = document.querySelector('.time-inputs');
                if (this.checked) {
                    timeInputs.classList.add('d-none');
                } else {
                    timeInputs.classList.remove('d-none');
                }
            });
            
            // Xử lý sự kiện khi loại sự kiện thay đổi
            document.getElementById('swal-event-type').addEventListener('change', function() {
                const badge = document.querySelector('.event-type-preview .badge');
                badge.style.backgroundColor = getBorderColorForEventType(this.value);
            });
            
            // Đảm bảo ngày kết thúc không sớm hơn ngày bắt đầu
            document.getElementById('swal-event-date').addEventListener('change', function() {
                try {
                    const startDate = new Date(this.value + 'T00:00:00');
                    const startDateDisplay = startDate.toLocaleDateString('vi-VN', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        timeZone: 'Asia/Ho_Chi_Minh'
                    });
                    
                    const displayElement = this.closest('.col-md-6').querySelector('.date-display-text');
                    if (displayElement) {
                        displayElement.textContent = `Hiển thị: ${startDateDisplay}`;
                    }
                    
                    // Cập nhật ngày kết thúc nếu cần
                    const endDateInput = document.getElementById('swal-event-end-date');
                    if (endDateInput && endDateInput.value === this.value) {
                        const endDisplayElement = endDateInput.closest('.col-md-6').querySelector('.date-display-text');
                        if (endDisplayElement) {
                            endDisplayElement.textContent = `Hiển thị: ${startDateDisplay}`;
                        }
                    }
                } catch (error) {
                    console.error("Lỗi cập nhật hiển thị ngày:", error);
                }
            });
            
            // Cập nhật hiển thị khi ngày kết thúc thay đổi
            document.getElementById('swal-event-end-date').addEventListener('change', function() {
                try {
                    const endDate = new Date(this.value);
                    const endDateDisplay = endDate.toLocaleDateString('vi-VN', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric'
                    });
                    
                    const displayElement = document.querySelector('#swal-event-end-date').closest('.col-md-6').querySelector('.date-display-text');
                    if (displayElement) {
                        displayElement.textContent = `Hiển thị: ${endDateDisplay}`;
                    }
    } catch (error) {
                    console.error("Lỗi cập nhật hiển thị ngày kết thúc:", error);
                }
            });
            
            // Đặt giá trị min cho ngày kết thúc
            document.getElementById('swal-event-end-date').min = document.getElementById('swal-event-date').value;
        },
        preConfirm: () => {
            try {
                // Lấy giá trị từ form
                const titleInput = document.getElementById('swal-event-title');
                const title = titleInput ? titleInput.value.trim() : '';
                
                const typeInput = document.getElementById('swal-event-type');
                const type = typeInput ? typeInput.value : 'other';
                
                const dateInput = document.getElementById('swal-event-date');
                const eventDate = dateInput ? dateInput.value : '';
                
                const endDateInput = document.getElementById('swal-event-end-date');
                const eventEndDate = endDateInput ? endDateInput.value : '';
                
                const allDayInput = document.getElementById('swal-all-day-event');
                const allDay = allDayInput ? allDayInput.checked : false;
                
                const startTimeInput = document.getElementById('swal-event-start-time');
                const startTime = startTimeInput ? startTimeInput.value : '';
                
                const endTimeInput = document.getElementById('swal-event-end-time');
                const endTime = endTimeInput ? endTimeInput.value : '';
                
                const descInput = document.getElementById('swal-event-description');
                const description = descInput ? descInput.value.trim() : '';
                
                console.log("Form values:", { title, type, eventDate, eventEndDate, allDay, startTime, endTime, description });
                
                // Kiểm tra tiêu đề
                if (!title) {
                    Swal.showValidationMessage('Vui lòng nhập tiêu đề sự kiện');
                    return false;
                }
                
                // Kiểm tra ngày
                if (!eventDate) {
                    Swal.showValidationMessage('Vui lòng chọn ngày bắt đầu');
                    return false;
                }
                
                if (!eventEndDate) {
                    Swal.showValidationMessage('Vui lòng chọn ngày kết thúc');
                    return false;
                }
                
                // Kiểm tra ngày kết thúc phải sau hoặc bằng ngày bắt đầu
                if (eventEndDate < eventDate) {
                    Swal.showValidationMessage('Ngày kết thúc phải sau hoặc bằng ngày bắt đầu');
                    return false;
                }
                
                // Kiểm tra thời gian nếu không phải cả ngày
                if (!allDay) {
                    if (!startTime) {
                        Swal.showValidationMessage('Vui lòng chọn thời gian bắt đầu');
                        return false;
                    }
                    
                    if (!endTime) {
                        Swal.showValidationMessage('Vui lòng chọn thời gian kết thúc');
                        return false;
                    }
                    
                    // Kiểm tra thời gian kết thúc > thời gian bắt đầu nếu cùng ngày
                    if (eventDate === eventEndDate && startTime >= endTime) {
                        Swal.showValidationMessage('Thời gian kết thúc phải sau thời gian bắt đầu');
                        return false;
                    }
                }
                
                // Tạo đối tượng ngày
                let start, end;
                
                if (allDay) {
                    // Nếu là sự kiện cả ngày
                    start = new Date(eventDate + 'T00:00:00');
                    end = new Date(eventEndDate + 'T23:59:59');
                    // Thêm 1 ngày vào ngày kết thúc vì FullCalendar tính ngày kết thúc là ngày tiếp theo
                    end.setDate(end.getDate() + 1);
                } else {
                    // Nếu có thời gian cụ thể
                    const [startHour, startMinute] = startTime.split(':');
                    const [endHour, endMinute] = endTime.split(':');
                    
                    start = new Date(eventDate);
                    start.setHours(parseInt(startHour), parseInt(startMinute), 0);
                    
                    end = new Date(eventEndDate);
                    end.setHours(parseInt(endHour), parseInt(endMinute), 0);
                }
                
                console.log("Event dates:", { start, end });
                
                // Trả về dữ liệu sự kiện
                return {
                    title: title,
                    type: type,
                    start: start,
                    end: end,
                    allDay: allDay,
                    description: description
                };
    } catch (error) {
                console.error("Error in preConfirm:", error);
                Swal.showValidationMessage('Đã xảy ra lỗi: ' + error.message);
                return false;
            }
        }
    }).then((result) => {
        if (result.isConfirmed && result.value) {
            const eventData = result.value;
            
            if (event) {
                // Cập nhật sự kiện hiện có
                updateEvent(event.id, eventData);
            } else {
                // Tạo sự kiện mới
                createEvent(eventData);
            }
        } else if (result.isDenied && event) {
            // Xóa sự kiện
            deleteEvent(event);
        }
    });
}

/**
 * Tạo sự kiện mới
 */
function createEvent(eventData) {
    console.log("Đang tạo sự kiện mới với dữ liệu:", eventData);
    
    // Hiển thị loading
    Swal.fire({
        title: 'Đang xử lý...',
        text: 'Đang tạo sự kiện mới',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Chuyển đổi đối tượng Date thành chuỗi ISO để gửi lên server
    const eventToSend = {
        title: eventData.title,
        type: eventData.type,
        start: eventData.start.toISOString().split('.')[0],
        end: eventData.end.toISOString().split('.')[0],
        allDay: eventData.allDay,
        description: eventData.description || ''
    };
    
    console.log("Dữ liệu gửi lên server:", eventToSend);
    
    // Lấy CSRF token từ cookie
    const csrftoken = getCookie('csrftoken');
    
    // Gửi request tạo sự kiện
    fetch('/dashboard/api/events/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(eventToSend)
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.error || `Lỗi HTTP: ${response.status} - ${response.statusText}`);
        }
        return data;
    })
    .then(data => {
        console.log("Sự kiện đã được tạo:", data);
        
        // Xác định màu cho sự kiện dựa vào loại
        const backgroundColor = getBorderColorForEventType(eventData.type);
        const borderColor = backgroundColor;
        
        // Thêm sự kiện vào lịch
        window.calendar.addEvent({
            id: data.id || new Date().getTime(),
            title: eventData.title,
            start: eventData.start,
            end: eventData.end,
            allDay: eventData.allDay,
            backgroundColor: backgroundColor,
            borderColor: borderColor,
            display: eventData.allDay ? 'block' : 'auto',
            extendedProps: {
                type: eventData.type,
                description: eventData.description || ''
            }
        });
        
        // Hiển thị thông báo thành công
        Swal.fire({
            icon: 'success',
            title: 'Thành công!',
            text: 'Sự kiện đã được tạo',
            confirmButtonColor: '#df2626',
            timer: 2000,
            timerProgressBar: true,
            showClass: {
                popup: 'animate__animated animate__fadeInDown'
            },
            hideClass: {
                popup: 'animate__animated animate__fadeOutUp'
            }
        });
        
        // Cập nhật lại lịch
        window.calendar.render();
        
        // Lưu ý: có thể cần làm mới lịch sau khi thêm sự kiện
        // window.calendar.refetchEvents();
    })
    .catch(error => {
        console.error("Chi tiết lỗi:", error);
        Swal.fire({
            icon: 'error',
            title: 'Lỗi!',
            text: error.message || 'Không thể tạo sự kiện. Vui lòng thử lại sau.',
            confirmButtonColor: '#df2626'
        });
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
 * Lấy màu viền cho từng loại sự kiện
 */
function getBorderColorForEventType(type) {
    // Log để debug
    console.log("Đang tìm màu cho loại sự kiện:", type);
    
    // Chuẩn hóa type để đảm bảo so sánh chính xác
    const normalizedType = type ? type.toLowerCase().trim() : 'other';
    
    // Cấu hình màu sắc rõ ràng hơn
    const colors = {
        'meeting': '#E63946',     // Đỏ
        'task': '#1D3557',        // Xanh đậm
        'deadline': '#F77F00',    // Cam
        'reminder': '#2A9D8F',    // Xanh lá
        'appointment': '#457B9D', // Xanh dương
        'other': '#6C757D'        // Xám (mặc định)
    };
    
    // Kiểm tra type có chứa từ khóa thay vì so sánh chính xác
    if (normalizedType.includes('meeting')) return colors['meeting'];
    if (normalizedType.includes('task')) return colors['task']; 
    if (normalizedType.includes('deadline')) return colors['deadline'];
    if (normalizedType.includes('reminder')) return colors['reminder'];
    if (normalizedType.includes('appointment')) return colors['appointment'];
    
    // Trả về màu mặc định nếu không tìm thấy
    console.log("Không tìm thấy màu phù hợp, sử dụng màu mặc định:", colors['other']);
    return colors['other'];
}

/**
 * Lấy text hiển thị cho từng loại sự kiện
 */
function getEventTypeText(type) {
    const eventTypes = {
        'meeting': 'Cuộc họp',
        'task': 'Công việc',
        'deadline': 'Hạn chót',
        'reminder': 'Nhắc nhở',
        'appointment': 'Cuộc hẹn',
        'other': 'Khác'
    };
    
    return eventTypes[type] || 'Khác';
}

/**
 * Lấy nội dung tooltip cho sự kiện
 */
function getEventTooltipContent(event) {
    const type = event.extendedProps?.type || 'other';
    const typeText = getEventTypeText(type);
    const description = event.extendedProps?.description || '';
    
    // Định dạng thời gian
    const startFormat = event.allDay ? 'DD/MM/YYYY' : 'DD/MM/YYYY HH:mm';
    const endFormat = event.allDay ? 'DD/MM/YYYY' : 'DD/MM/YYYY HH:mm';
    
    const start = moment(event.start).format(startFormat);
    const end = event.end ? moment(event.end).format(endFormat) : '';
    const timeInfo = event.allDay 
        ? (end ? `Cả ngày (${start} - ${end})` : `Cả ngày ${start}`) 
        : (end ? `${start} - ${end}` : start);
    
    return `
        <div class="event-tooltip">
            <div style="font-weight:bold; margin-bottom:5px;">${event.title}</div>
            <div style="margin-bottom:3px;"><i class="far fa-clock mr-1"></i> ${timeInfo}</div>
            <div style="margin-bottom:3px;"><i class="far fa-bookmark mr-1"></i> ${typeText}</div>
            ${description ? `<div style="border-top:1px solid #eee; padding-top:5px; margin-top:5px;">${description}</div>` : ''}
        </div>
    `;
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

/**
 * Hiển thị chi tiết đơn hàng
 */
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

    // Format tiền tệ
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', { 
            style: 'decimal',
            maximumFractionDigits: 0
        }).format(amount) + 'đ';
    };
    
    Swal.fire({
        title: `<div class="order-detail-title">
                    <i class="fas fa-shopping-cart text-primary mr-2"></i>
                    Chi tiết đơn hàng #${orderId}
                </div>`,
        html: `
            <div class="order-details-container">
                <!-- Thông tin khách hàng -->
                <div class="order-detail-block customer-block">
                    <div class="block-header">
                        <i class="fas fa-user-circle text-primary"></i>
                        <h5>Thông tin khách hàng</h5>
                </div>
                    <div class="block-content">
                        <div class="info-item">
                            <div class="info-label"><i class="fas fa-user text-muted"></i> Tên:</div>
                            <div class="info-value">${orderData.customer}</div>
                </div>
                        <div class="info-item">
                            <div class="info-label"><i class="fas fa-phone text-muted"></i> SĐT:</div>
                            <div class="info-value">${orderData.phone}</div>
                </div>
                        <div class="info-item">
                            <div class="info-label"><i class="fas fa-envelope text-muted"></i> Email:</div>
                            <div class="info-value">${orderData.email}</div>
                </div>
                        <div class="info-item">
                            <div class="info-label"><i class="fas fa-map-marker-alt text-muted"></i> Địa chỉ:</div>
                            <div class="info-value">${orderData.address}</div>
                </div>
                </div>
                </div>

                <!-- Thông tin đơn hàng -->
                <div class="order-detail-block order-block">
                    <div class="block-header">
                        <i class="fas fa-info-circle text-info"></i>
                        <h5>Thông tin đơn hàng</h5>
                    </div>
                    <div class="block-content">
                        <div class="info-item">
                            <div class="info-label"><i class="fas fa-calendar-alt text-muted"></i> Ngày đặt:</div>
                            <div class="info-value">${orderData.date}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label"><i class="fas fa-check-circle text-muted"></i> Trạng thái:</div>
                            <div class="info-value">
                                <span class="badge badge-success">${orderData.status}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sản phẩm -->
                <div class="order-detail-block products-block">
                    <div class="block-header">
                        <i class="fas fa-box-open text-warning"></i>
                        <h5>Sản phẩm</h5>
                    </div>
                    <div class="block-content">
                        <table class="table table-striped product-table">
                            <thead>
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
                                        <td class="text-right">${formatCurrency(p.price)}</td>
                                        <td class="text-right">${formatCurrency(p.price * p.quantity)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                            <tfoot>
                                <tr class="total-row">
                                    <td colspan="3" class="text-right font-weight-bold">Tổng cộng:</td>
                                    <td class="text-right font-weight-bold">${formatCurrency(orderData.total)}</td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            </div>
        `,
        width: '700px',
        padding: '0',
        background: '#fff',
        showCloseButton: true,
        showConfirmButton: false,
        customClass: {
            container: 'order-detail-container',
            popup: 'order-detail-popup',
            header: 'order-detail-header',
            closeButton: 'order-detail-close'
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

/**
 * Cập nhật sự kiện
 */
function updateEvent(eventId, eventData) {
    console.log("Đang cập nhật sự kiện:", eventId, eventData);
    
    // Hiển thị loading
    Swal.fire({
        title: 'Đang xử lý...',
        text: 'Đang cập nhật sự kiện',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    // Chuyển đổi đối tượng Date thành chuỗi ISO để gửi lên server
    const eventToSend = {
        id: eventId,
        title: eventData.title,
        type: eventData.type,
        start: eventData.start.toISOString().split('.')[0],
        end: eventData.end.toISOString().split('.')[0],
        allDay: eventData.allDay,
        description: eventData.description || ''
    };
    
    console.log("Dữ liệu gửi lên server:", eventToSend);
    
    // Lấy CSRF token từ cookie
    const csrftoken = getCookie('csrftoken');
    
    // Thử phương thức PUT thay vì POST (vì lỗi 405)
    fetch(`/dashboard/api/events/${eventId}/update/`, {
        method: 'PUT', // Đổi từ POST sang PUT
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(eventToSend)
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            // Nếu PUT không hoạt động, thử xuống các phương thức khác
            if (response.status === 405) {
                throw new Error('API yêu cầu phương thức khác. Vui lòng kiểm tra document API hoặc liên hệ quản trị viên.');
            }
            throw new Error(data.error || `Lỗi HTTP: ${response.status} - ${response.statusText}`);
        }
        return data;
    })
    .then(data => {
        console.log("Sự kiện đã được cập nhật:", data);
        
        // Lấy sự kiện hiện tại từ lịch
        const event = window.calendar.getEventById(eventId);
        if (event) {
            // Trước khi cập nhật, xóa sự kiện cũ
            event.remove();
            
            // Tạo sự kiện mới với thông tin đã cập nhật
            window.calendar.addEvent({
                id: eventId,
                title: eventData.title,
                start: eventData.start,
                end: eventData.end,
                allDay: eventData.allDay,
                backgroundColor: getBorderColorForEventType(eventData.type),
                borderColor: getBorderColorForEventType(eventData.type),
                display: eventData.allDay ? 'block' : 'auto',
                extendedProps: {
                    type: eventData.type,
                    description: eventData.description || ''
                }
            });
        }
        
        // Hiển thị thông báo thành công với animation
            Swal.fire({
                icon: 'success',
            title: 'Thành công!',
            text: 'Sự kiện đã được cập nhật',
            confirmButtonColor: '#df2626',
            timer: 2000,
            timerProgressBar: true,
            showClass: {
                popup: 'animate__animated animate__fadeInDown'
            },
            hideClass: {
                popup: 'animate__animated animate__fadeOutUp'
            }
        });
        
        // Cập nhật lại lịch để đảm bảo hiển thị đúng
        window.calendar.render();
    })
    .catch(error => {
        console.error("Chi tiết lỗi:", error);
        Swal.fire({
            icon: 'error',
            title: 'Lỗi!',
            text: error.message || 'Không thể cập nhật sự kiện. Vui lòng thử lại sau.',
                confirmButtonColor: '#df2626'
            });
    });
}

/**
 * Cập nhật sự kiện sau khi kéo thả
 */
function updateEventAfterDrag(event) {
    console.log("Cập nhật sau khi kéo thả:", event);
    
    const eventData = {
        title: event.title,
        type: event.extendedProps.type || 'other',
        start: event.start,
        end: event.end || new Date(event.start.getTime() + 3600000), // Mặc định thêm 1 giờ nếu không có end
        allDay: event.allDay,
        description: event.extendedProps.description || ''
    };
    
    updateEvent(event.id, eventData);
}

/**
 * Thêm nút tạo sự kiện nổi ở góc dưới bên phải
 */
function addFloatingAddButton() {
    // Kiểm tra xem nút đã tồn tại chưa
    if (document.querySelector('.floating-add-button')) {
        document.querySelector('.floating-add-button').remove();
    }
    
    // Tạo nút
    const addButton = document.createElement('button');
    addButton.className = 'floating-add-button';
    addButton.innerHTML = '<i class="fas fa-plus"></i>';
    addButton.title = 'Tạo sự kiện mới';
    
    // Thêm sự kiện click
    addButton.addEventListener('click', function() {
        // Sử dụng showEventForm nếu showCreateEventModal không tồn tại
        if (typeof showCreateEventModal === 'function') {
            showCreateEventModal();
        } else if (typeof showEventForm === 'function') {
            showEventForm();
        } else {
            console.error('Không tìm thấy hàm tạo sự kiện');
            Swal.fire({
                icon: 'error',
                title: 'Lỗi',
                text: 'Không thể tạo sự kiện mới. Vui lòng tải lại trang.',
                confirmButtonColor: '#df2626'
            });
        }
    });
    
    // Thêm vào body
    document.body.appendChild(addButton);
    
    console.log("Đã thêm nút Add Event cố định");
}

// Thêm event listener để force màu sắc khi DOM load xong
document.addEventListener('DOMContentLoaded', () => {
    // Force màu sắc sau khi trang load xong
    setTimeout(() => {
        document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(el => {
            const typeMatch = Array.from(el.classList)
                .find(cls => cls.startsWith('fc-event-type-'));
            
            if (typeMatch) {
                const eventType = typeMatch.replace('fc-event-type-', '');
                const color = getBorderColorForEventType(eventType);
                
                el.style.cssText = `
                    background-color: ${color} !important;
                    border-color: ${color} !important;
                    color: white !important;
                `;
                
                el.querySelectorAll('*').forEach(child => {
                    child.style.cssText = `
                        color: white !important;
                        font-weight: 500 !important;
                    `;
                });
            }
        });
    }, 500);
});

// Thêm đoạn code theo dõi DOM và force màu sắc liên tục
function setupEventColoringObserver() {
    console.log("Đang thiết lập observer theo dõi màu sắc sự kiện...");
    
    // Tạo một MutationObserver để theo dõi DOM thay đổi
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            // Kiểm tra nếu có node mới được thêm vào
            if (mutation.addedNodes.length) {
                // Lặp qua các node đã thêm
                mutation.addedNodes.forEach(function(node) {
                    // Kiểm tra xem node có phải là element không
                    if (node.nodeType === 1) {
                        // Xử lý nếu đây là event
                        if (node.classList && (node.classList.contains('fc-event') || 
                            node.classList.contains('fc-daygrid-event'))) {
                            applyEventColor(node);
                        }
                        
                        // Tìm kiếm các event bên trong node
                        const events = node.querySelectorAll('.fc-event, .fc-daygrid-event');
                        events.forEach(applyEventColor);
                    }
                });
            }
            
            // Nếu có thay đổi thuộc tính của các node hiện có
            if (mutation.type === 'attributes' && mutation.target.nodeType === 1) {
                const el = mutation.target;
                if (el.classList && (el.classList.contains('fc-event') || 
                    el.classList.contains('fc-daygrid-event'))) {
                    applyEventColor(el);
                }
            }
        });
    });
    
    // Bắt đầu theo dõi toàn bộ DOM với cấu hình
    observer.observe(document.body, {
        childList: true,     // Theo dõi thêm/xóa node
        subtree: true,       // Theo dõi toàn bộ cây DOM
        attributes: true,    // Theo dõi thay đổi thuộc tính
        attributeFilter: ['class'] // Chỉ quan tâm đến thay đổi class
    });
    
    console.log("Đã thiết lập observer thành công!");
    
    // Áp dụng màu sắc ngay lập tức cho tất cả sự kiện hiện có
    document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(applyEventColor);
    
    return observer;
}

// Hàm áp dụng màu sắc cho một sự kiện
function applyEventColor(el) {
    // Xác định loại sự kiện
    let eventType = 'other';
    
    // Tìm kiếm trong các data attributes
    if (el.getAttribute('data-fc-event-type')) {
        eventType = el.getAttribute('data-fc-event-type');
    }
    
    // Tìm kiếm trong class
    const classNames = el.className.split(' ');
    for (const cls of classNames) {
        if (cls.includes('meeting')) eventType = 'meeting';
        else if (cls.includes('task')) eventType = 'task'; 
        else if (cls.includes('deadline')) eventType = 'deadline';
        else if (cls.includes('reminder')) eventType = 'reminder';
        else if (cls.includes('appointment')) eventType = 'appointment';
    }
    
    // Lấy màu tương ứng
    const color = getBorderColorForEventType(eventType);
    console.log("Áp dụng màu", color, "cho sự kiện loại", eventType);
    
    // Sử dụng !important ở cấp cao nhất có thể
    el.style = `
        background-color: ${color} !important;
        border-color: ${color} !important;
        color: white !important;
    `;
    
    // Ghi đè style cho tất cả các phần tử con
    Array.from(el.querySelectorAll('*')).forEach(child => {
        child.style = `color: white !important;`;
    });
    
    // Đánh dấu đã xử lý
    el.setAttribute('data-event-colored', 'true');
}

// Khởi chạy observer khi trang load xong
document.addEventListener('DOMContentLoaded', function() {
    // Đăng ký observer để theo dõi DOM
    const observer = setupEventColoringObserver();
    
    // Force một lần nữa sau khi trang đã load hoàn toàn
    setTimeout(() => {
        document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(applyEventColor);
    }, 1000);
    
    // Force lại một lần nữa để đảm bảo
    setTimeout(() => {
        document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(applyEventColor);
    }, 2000);
});

// Tạo một interval để liên tục kiểm tra và áp dụng màu sắc
setInterval(function() {
    document.querySelectorAll('.fc-event, .fc-daygrid-event').forEach(el => {
        applyEventColor(el);
    });
}, 1000); // Kiểm tra mỗi 1 giây