from django.core.management.base import BaseCommand
import os
import glob
import shutil
import time

class Command(BaseCommand):
    help = 'Reset migrations của store app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang reset migrations của store app...')
        
        # Xóa các file migrations cũ của store app
        migrations_dir = 'store/migrations'
        migration_files = glob.glob(f'{migrations_dir}/[0-9]*.py')
        migration_files += glob.glob(f'{migrations_dir}/[0-9]*.pyc')
        migration_files += glob.glob(f'{migrations_dir}/__pycache__/[0-9]*.*.pyc')
        
        for file in migration_files:
            try:
                os.remove(file)
                self.stdout.write(f'Đã xóa file: {file}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Không thể xóa {file}: {str(e)}'))
        
        # Xóa các bản ghi migration trong database
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem bảng django_migrations có tồn tại không
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
                if cursor.fetchone():
                    cursor.execute("DELETE FROM django_migrations WHERE app='store'")
                    self.stdout.write('Đã xóa bản ghi migration của store app trong database')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Lỗi khi xóa migration records: {str(e)}'))
        
        # Tạo file migration mới với nội dung cơ bản
        initial_migration_path = os.path.join(migrations_dir, '0001_initial.py')
        try:
            with open(initial_migration_path, 'w', encoding='utf-8') as f:
                f.write("""# Generated manually

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('original_price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]
""")
            self.stdout.write(f'Đã tạo file migration cơ bản: {initial_migration_path}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Lỗi khi tạo file migration cơ bản: {str(e)}'))
        
        # Đánh dấu migration đã được áp dụng
        try:
            with connection.cursor() as cursor:
                # Kiểm tra xem bảng django_migrations có tồn tại không
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
                if cursor.fetchone():
                    # Thêm bản ghi cho migration mới
                    cursor.execute(
                        "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
                        ['store', '0001_initial', time.strftime('%Y-%m-%d %H:%M:%S')]
                    )
                    self.stdout.write('Đã đánh dấu migration 0001_initial đã được áp dụng')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Lỗi khi đánh dấu migration đã áp dụng: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Đã reset xong migrations của store app!')) 