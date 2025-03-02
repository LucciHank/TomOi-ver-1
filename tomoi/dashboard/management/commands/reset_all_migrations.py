from django.core.management.base import BaseCommand
import os
import glob
import time
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Reset tất cả migrations của dự án'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang reset tất cả migrations...')
        
        # Danh sách các app cần reset migration
        apps = ['accounts', 'store', 'dashboard', 'payment', 'blog']
        
        # Xóa tất cả các file migrations
        for app in apps:
            migrations_dir = f'{app}/migrations'
            if not os.path.exists(migrations_dir):
                continue
                
            migration_files = glob.glob(f'{migrations_dir}/[0-9]*.py')
            migration_files += glob.glob(f'{migrations_dir}/[0-9]*.pyc')
            migration_files += glob.glob(f'{migrations_dir}/__pycache__/[0-9]*.*.pyc')
            
            for file in migration_files:
                try:
                    os.remove(file)
                    self.stdout.write(f'Đã xóa file: {file}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Không thể xóa {file}: {str(e)}'))
        
        # Xóa database nếu là SQLite
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite3' in db_engine:
            db_path = settings.DATABASES['default']['NAME']
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                    self.stdout.write(f'Đã xóa database: {db_path}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Không thể xóa database: {str(e)}'))
        else:
            # Nếu không phải SQLite, xóa các bản ghi migration
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
                    if cursor.fetchone():
                        cursor.execute("DELETE FROM django_migrations")
                        self.stdout.write('Đã xóa tất cả bản ghi migration trong database')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Lỗi khi xóa migration records: {str(e)}'))
        
        # Tạo migrations mới
        from django.core.management import call_command
        for app in apps:
            try:
                call_command('makemigrations', app)
                self.stdout.write(f'Đã tạo migration mới cho {app}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Lỗi khi tạo migration cho {app}: {str(e)}'))
        
        # Thực hiện migrate
        try:
            call_command('migrate', '--fake-initial')
            call_command('migrate')
            self.stdout.write('Đã thực hiện migrate thành công')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi khi thực hiện migrate: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('Đã reset xong tất cả migrations!'))