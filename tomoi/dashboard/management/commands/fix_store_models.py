from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Sửa lỗi cấu trúc bảng store_productvariant'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang sửa lỗi cấu trúc bảng store_productvariant...')
        
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem cột original_price đã tồn tại chưa
                cursor.execute("SELECT name FROM pragma_table_info('store_productvariant') WHERE name='original_price'")
                if cursor.fetchone():
                    self.stdout.write('Cột original_price đã tồn tại, bỏ qua')
                else:
                    self.stdout.write('Thêm cột original_price vào bảng store_productvariant')
                    cursor.execute("ALTER TABLE store_productvariant ADD COLUMN original_price decimal(10,2) NULL")
                    # Cập nhật giá trị mặc định
                    cursor.execute("UPDATE store_productvariant SET original_price = price WHERE original_price IS NULL")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Đã sửa xong cấu trúc bảng store_productvariant!')) 