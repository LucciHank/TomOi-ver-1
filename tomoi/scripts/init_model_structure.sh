#!/bin/bash
# Script để cài đặt cấu trúc models mới

# Dừng server Django nếu đang chạy
# Sao lưu models.py ban đầu
echo "Sao lưu file models.py gốc"
cp dashboard/models.py dashboard/models.py.bak

# Tạo thư mục models nếu chưa tồn tại
echo "Tạo cấu trúc thư mục mới"
mkdir -p dashboard/models

# Kiểm tra và tạo file __init__.py
if [ ! -f dashboard/models/__init__.py ]; then
    echo "Tạo file __init__.py"
    echo "# Import mọi model cần thiết từ các file khác" > dashboard/models/__init__.py
    echo "from .base import *" >> dashboard/models/__init__.py
    echo "from .discount import *" >> dashboard/models/__init__.py
    echo "from .subscription import *" >> dashboard/models/__init__.py
    echo "from .warranty import *" >> dashboard/models/__init__.py
fi

# Xóa các file .pyc để tránh cache
echo "Xóa các file cache .pyc"
find . -name "*.pyc" -delete

# Tạo migrations mới cho cấu trúc đã thay đổi
echo "Tạo migrations cho cấu trúc mới"
python manage.py makemigrations

# Áp dụng migrations
echo "Áp dụng migrations"
python manage.py migrate

echo "Hoàn thành cài đặt cấu trúc models mới!" 