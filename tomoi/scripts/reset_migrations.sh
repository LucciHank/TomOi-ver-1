#!/bin/bash

echo "=== Đang xóa các file migrations cũ ==="
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo "=== Đang xóa file database.db ==="
if [ -f db.sqlite3 ]; then
    echo "Xóa db.sqlite3"
    rm -f db.sqlite3
fi

echo "=== Tạo migration mới ==="
python manage.py makemigrations accounts
python manage.py makemigrations store
python manage.py makemigrations dashboard
python manage.py makemigrations payment
python manage.py makemigrations blog

echo "=== Thực hiện migrate ==="
python manage.py migrate --fake-initial
python manage.py migrate

echo "=== Khởi tạo dữ liệu mẫu ==="
python manage.py init_db

echo "=== Hoàn tất! ===" 