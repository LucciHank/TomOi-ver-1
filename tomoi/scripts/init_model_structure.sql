-- Kiểm tra và tạo cấu trúc bảng Source
CREATE TABLE IF NOT EXISTS dashboard_source (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    source_url VARCHAR(255),
    platform VARCHAR(50),
    product_type VARCHAR(100),
    base_price DECIMAL(10, 2),
    priority VARCHAR(20),
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- Kiểm tra và tạo cấu trúc bảng SourceProduct
CREATE TABLE IF NOT EXISTS dashboard_sourceproduct (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    name VARCHAR(100),
    description TEXT,
    product_url VARCHAR(255),
    price DECIMAL(10, 2),
    error_rate INTEGER,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (source_id) REFERENCES dashboard_source (id),
    FOREIGN KEY (product_id) REFERENCES store_product (id)
);

-- Kiểm tra và tạo cấu trúc bảng SourceLog
CREATE TABLE IF NOT EXISTS dashboard_sourcelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    source_product_id INTEGER,
    log_type VARCHAR(50),
    has_stock BOOLEAN,
    processing_time INTEGER,
    notes TEXT,
    created_by_id INTEGER,
    created_at DATETIME,
    FOREIGN KEY (source_id) REFERENCES dashboard_source (id),
    FOREIGN KEY (source_product_id) REFERENCES dashboard_sourceproduct (id),
    FOREIGN KEY (created_by_id) REFERENCES auth_user (id)
);

-- Kiểm tra và tạo cấu trúc bảng WarrantyTicket
CREATE TABLE IF NOT EXISTS dashboard_warrantyticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product_id INTEGER,
    issue_description TEXT,
    status VARCHAR(20),
    assigned_to_id INTEGER,
    resolution TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES accounts_customuser (id),
    FOREIGN KEY (product_id) REFERENCES store_product (id),
    FOREIGN KEY (assigned_to_id) REFERENCES accounts_customuser (id)
);

-- Kiểm tra và tạo cấu trúc bảng WarrantyHistory
CREATE TABLE IF NOT EXISTS dashboard_warrantyhistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    action VARCHAR(100),
    notes TEXT,
    performed_by_id INTEGER,
    created_at DATETIME,
    FOREIGN KEY (ticket_id) REFERENCES dashboard_warrantyticket (id),
    FOREIGN KEY (performed_by_id) REFERENCES accounts_customuser (id)
); 