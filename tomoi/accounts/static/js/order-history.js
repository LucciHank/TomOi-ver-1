document.addEventListener('DOMContentLoaded', function() {
    const filterForm = document.getElementById('filterForm');
    const tableRows = document.querySelectorAll('table tbody tr');

    // Xử lý sự kiện submit form
    filterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        filterTable();
    });

    // Xử lý sự kiện reset form
    filterForm.addEventListener('reset', function(e) {
        setTimeout(() => {
            filterTable();
        }, 0);
    });

    function getDateFromStr(dateStr) {
        // Format: "dd/mm/yyyy hh:mm"
        const [date, time] = dateStr.split(' ');
        const [day, month, year] = date.split('/');
        const [hours, minutes] = time.split(':');
        
        // Tạo Date object với các thành phần đã parse
        return new Date(year, month - 1, day, hours, minutes);
    }

    function filterTable() {
        const formData = new FormData(filterForm);
        
        // Lấy và xử lý các giá trị từ form
        const dateFrom = formData.get('date_from');
        const dateTo = formData.get('date_to');
        
        // Convert sang Date objects nếu có giá trị
        const startDate = dateFrom ? new Date(dateFrom) : null;
        const endDate = dateTo ? new Date(dateTo) : null;
        
        // Set endDate về cuối ngày nếu có
        if (endDate) {
            endDate.setHours(23, 59, 59, 999);
        }

        const filters = {
            orderId: formData.get('order_id').toLowerCase(),
            status: formData.get('status'),
            startDate: startDate,
            endDate: endDate,
            amountMin: formData.get('amount_min'),
            amountMax: formData.get('amount_max'),
            paymentMethod: formData.get('payment_method')
        };

        tableRows.forEach(row => {
            const cells = row.getElementsByTagName('td');
            const rowDate = getDateFromStr(cells[1].textContent);
            
            const rowData = {
                orderId: cells[0].textContent.toLowerCase(),
                date: rowDate,
                amount: parseFloat(cells[2].textContent.replace(/[^\d]/g, '')),
                status: cells[3].textContent.trim(),
                paymentMethod: cells[4].textContent.toLowerCase()
            };

            let showRow = true;

            // Lọc theo mã đơn hàng
            if (filters.orderId && !rowData.orderId.includes(filters.orderId)) {
                showRow = false;
            }

            // Lọc theo trạng thái
            if (filters.status && rowData.status !== filters.status) {
                showRow = false;
            }

            // Lọc theo khoảng thời gian
            if (filters.startDate && rowData.date < filters.startDate) {
                showRow = false;
            }
            if (filters.endDate && rowData.date > filters.endDate) {
                showRow = false;
            }

            // Lọc theo khoảng số tiền
            if (filters.amountMin && rowData.amount < parseFloat(filters.amountMin)) {
                showRow = false;
            }
            if (filters.amountMax && rowData.amount > parseFloat(filters.amountMax)) {
                showRow = false;
            }

            // Lọc theo phương thức thanh toán
            if (filters.paymentMethod && !rowData.paymentMethod.includes(filters.paymentMethod.toLowerCase())) {
                showRow = false;
            }

            row.style.display = showRow ? '' : 'none';
        });

        // Log để debug
        console.log('Filters:', filters);
    }
}); 