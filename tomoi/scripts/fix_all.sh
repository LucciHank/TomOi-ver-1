#!/bin/bash

echo "=== Đang reset migrations của store app ==="
python manage.py reset_store_migrations

echo "=== Đang sửa lỗi dependencies trong migration files ==="
python manage.py fix_migration_dependencies

echo "=== Đang sửa lỗi cột original_price ==="
python manage.py fix_productvariant

echo "=== Đang sửa lỗi cấu trúc database ==="
python manage.py fix_database

echo "=== Đang khởi tạo cấu trúc model ==="
python manage.py init_model_structure

echo "=== Đang thực hiện migrate ==="
python manage.py migrate --fake-initial
python manage.py migrate

echo "=== Hoàn tất! ===" 