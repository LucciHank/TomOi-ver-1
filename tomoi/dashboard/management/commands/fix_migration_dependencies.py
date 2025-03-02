from django.core.management.base import BaseCommand
import os
import glob
import re

class Command(BaseCommand):
    help = 'Sửa lỗi dependencies trong migration files'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang sửa lỗi dependencies trong migration files...')
        
        # Tìm tất cả các file migration của store app
        migrations_dir = 'store/migrations'
        migration_files = glob.glob(f'{migrations_dir}/[0-9]*.py')
        
        for file_path in migration_files:
            try:
                # Đọc nội dung file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Tìm và sửa dependencies
                if "('store', '0001_productvariant_original_price_and_more')" in content:
                    self.stdout.write(f'Sửa dependencies trong file: {file_path}')
                    
                    # Thay thế dependencies
                    modified_content = content.replace(
                        "('store', '0001_productvariant_original_price_and_more')",
                        "('store', '0001_initial')"
                    )
                    
                    # Ghi lại file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    
                    self.stdout.write(self.style.SUCCESS(f'Đã sửa file: {file_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Lỗi khi sửa file {file_path}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Đã sửa xong dependencies trong migration files!')) 