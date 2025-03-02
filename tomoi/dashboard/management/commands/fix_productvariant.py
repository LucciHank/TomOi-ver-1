from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Sửa lỗi cụ thể trong bảng store_productvariant'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang sửa lỗi cột original_price trong bảng store_productvariant...')
        
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem bảng có tồn tại không
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='store_productvariant'")
                if not cursor.fetchone():
                    self.stdout.write('Bảng store_productvariant chưa tồn tại')
                    return

                # Kiểm tra cấu trúc bảng
                cursor.execute("PRAGMA table_info(store_productvariant)")
                columns = {col[1] for col in cursor.fetchall()}
                
                if 'original_price' not in columns:
                    self.stdout.write('Thêm cột original_price vào bảng store_productvariant')
                    cursor.execute("ALTER TABLE store_productvariant ADD COLUMN original_price decimal(10,2) NULL")
                
                # Cập nhật giá trị nếu cột price tồn tại
                if 'price' in columns:
                    cursor.execute("UPDATE store_productvariant SET original_price = price WHERE original_price IS NULL")
                
                # Xóa migration record cũ nếu có
                cursor.execute("SELECT name FROM django_migrations WHERE app='store' AND name LIKE '%productvariant_original_price%'")
                if cursor.fetchone():
                    cursor.execute("DELETE FROM django_migrations WHERE app='store' AND name LIKE '%productvariant_original_price%'")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Đã sửa xong lỗi cột original_price!')) 