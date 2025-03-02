from django.core.management.base import BaseCommand
from django.db import connection
import os
import glob

class Command(BaseCommand):
    help = 'Sửa lỗi migration và cấu trúc database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang sửa lỗi migration...')
        
        # Xóa file migration cụ thể gây lỗi
        migration_files = glob.glob('store/migrations/0001_productvariant_original_price*.py')
        for file in migration_files:
            if os.path.exists(file):
                self.stdout.write(f'Xóa file migration gây lỗi: {file}')
                os.remove(file)
        
        # Sửa lỗi cột original_price trong ProductVariant
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
            self.stdout.write(self.style.ERROR(f'Lỗi khi sửa bảng store_productvariant: {str(e)}'))
        
        # Sửa lỗi cột created_at trong Campaign
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem bảng dashboard_campaign có tồn tại không
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_campaign'")
                if cursor.fetchone():
                    # Kiểm tra xem cột created_at đã tồn tại chưa
                    cursor.execute("SELECT name FROM pragma_table_info('dashboard_campaign') WHERE name='created_at'")
                    if not cursor.fetchone():
                        self.stdout.write('Thêm cột created_at vào bảng dashboard_campaign')
                        cursor.execute("ALTER TABLE dashboard_campaign ADD COLUMN created_at datetime NULL")
                        cursor.execute("UPDATE dashboard_campaign SET created_at = start_date WHERE created_at IS NULL")
                else:
                    self.stdout.write('Bảng dashboard_campaign không tồn tại, bỏ qua')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi khi sửa bảng dashboard_campaign: {str(e)}'))
        
        # Cập nhật django_migrations để tránh lỗi khi migrate
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem migration đã được áp dụng chưa
                cursor.execute("SELECT name FROM django_migrations WHERE app='store' AND name LIKE '%productvariant_original_price%'")
                if cursor.fetchone():
                    self.stdout.write('Xóa bản ghi migration gây lỗi trong django_migrations')
                    cursor.execute("DELETE FROM django_migrations WHERE app='store' AND name LIKE '%productvariant_original_price%'")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi khi cập nhật django_migrations: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Đã sửa xong lỗi migration!')) 