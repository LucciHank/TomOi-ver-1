from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Sửa lỗi cấu trúc bảng dashboard_campaign'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang sửa lỗi cấu trúc bảng dashboard_campaign...')
        
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem bảng dashboard_campaign có tồn tại không
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_campaign'")
                if not cursor.fetchone():
                    self.stdout.write(self.style.WARNING('Bảng dashboard_campaign không tồn tại, bỏ qua'))
                    return
                
                # Kiểm tra xem cột created_at đã tồn tại chưa
                cursor.execute("SELECT name FROM pragma_table_info('dashboard_campaign') WHERE name='created_at'")
                if cursor.fetchone():
                    self.stdout.write('Cột created_at đã tồn tại, bỏ qua')
                else:
                    self.stdout.write('Thêm cột created_at vào bảng dashboard_campaign')
                    cursor.execute("ALTER TABLE dashboard_campaign ADD COLUMN created_at datetime NULL")
                    cursor.execute("UPDATE dashboard_campaign SET created_at = start_date WHERE created_at IS NULL")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Hoàn thành sửa lỗi cấu trúc bảng dashboard_campaign'))
    