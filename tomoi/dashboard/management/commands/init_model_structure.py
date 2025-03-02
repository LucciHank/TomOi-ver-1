from django.core.management.base import BaseCommand
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Khởi tạo cấu trúc model cho hệ thống'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang khởi tạo cấu trúc model...')
        
        # Thực hiện các lệnh SQL từ file
        script_path = os.path.join('scripts', 'init_model_structure.sql')
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
        
        self.stdout.write(self.style.SUCCESS('Đã khởi tạo xong cấu trúc model!')) 