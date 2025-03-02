-- Kiểm tra và sửa lỗi bảng Campaign
SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_campaign';
-- Nếu bảng tồn tại, thêm cột created_at
ALTER TABLE dashboard_campaign ADD COLUMN created_at datetime NULL;
UPDATE dashboard_campaign SET created_at = start_date WHERE created_at IS NULL;

-- Kiểm tra và sửa lỗi cột original_price trong ProductVariant
SELECT name FROM sqlite_master WHERE type='table' AND name='store_productvariant';
SELECT name FROM pragma_table_info('store_productvariant') WHERE name='original_price';
-- Nếu bảng tồn tại và cột chưa tồn tại, thêm cột original_price
ALTER TABLE store_productvariant ADD COLUMN original_price decimal(10,2) NULL;
-- Cập nhật giá trị mặc định từ cột price nếu có
UPDATE store_productvariant SET original_price = price WHERE original_price IS NULL AND price IS NOT NULL; 