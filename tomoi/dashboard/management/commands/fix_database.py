from django.core.management.base import BaseCommand
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Sửa lỗi cấu trúc database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang sửa lỗi cấu trúc database...')
        
        # Thực hiện các lệnh SQL từ file migration.sql
        script_path = os.path.join('scripts', 'migration.sql')
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                
            with connection.cursor() as cursor:
                # Chia thành từng lệnh SQL
                for sql in sql_script.split(';'):
                    sql = sql.strip()
                    if sql and not sql.startswith('--'):
                        try:
                            self.stdout.write(f'Executing: {sql}')
                            cursor.execute(sql)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Lỗi khi thực hiện: {sql}'))
                            self.stdout.write(self.style.WARNING(f'Chi tiết lỗi: {str(e)}'))
        
        # Sửa lỗi cột original_price trong ProductVariant
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem cột original_price đã tồn tại chưa
                cursor.execute("SELECT name FROM pragma_table_info('store_productvariant') WHERE name='original_price'")
                if not cursor.fetchone():
                    self.stdout.write('Thêm cột original_price vào bảng store_productvariant')
                    cursor.execute("ALTER TABLE store_productvariant ADD COLUMN original_price decimal(10,2) NULL")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Lỗi khi sửa bảng store_productvariant: {str(e)}'))
        
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
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Lỗi khi sửa bảng dashboard_campaign: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Đã sửa xong cấu trúc database!')) 