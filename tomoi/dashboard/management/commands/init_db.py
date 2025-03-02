from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from dashboard.models.source import Source, SourceProduct, SourceLog
from store.models import Product
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Khởi tạo dữ liệu mẫu cho hệ thống quản lý nguồn nhập'

    def handle(self, *args, **kwargs):
        self.stdout.write('Đang khởi tạo dữ liệu mẫu...')
        
        # Tạo dữ liệu mẫu cho Source
        platforms = ['facebook', 'zalo', 'telegram', 'website', 'other']
        product_types = ['Game Account', 'Premium Account', 'Software License', 'Digital Content']
        priorities = ['high', 'medium', 'low']
        
        # Xóa dữ liệu cũ
        Source.objects.all().delete()
        
        # Tạo nguồn mẫu
        sources = []
        for i in range(1, 11):
            source = Source.objects.create(
                name=f'Nguồn {i}',
                source_url=f'https://example.com/source{i}',
                platform=random.choice(platforms),
                product_type=random.choice(product_types),
                base_price=random.randint(50000, 500000),
                priority=random.choice(priorities),
                notes=f'Ghi chú cho nguồn {i}'
            )
            sources.append(source)
            self.stdout.write(f'Đã tạo nguồn: {source.name}')
        
        # Tạo sản phẩm mẫu nếu chưa có
        if Product.objects.count() == 0:
            for i in range(1, 6):
                product = Product.objects.create(
                    name=f'Sản phẩm {i}',
                    description=f'Mô tả sản phẩm {i}',
                    price=random.randint(100000, 1000000),
                    stock=random.randint(10, 100)
                )
                self.stdout.write(f'Đã tạo sản phẩm: {product.name}')
        
        products = Product.objects.all()
        
        # Tạo SourceProduct
        for source in sources:
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                price = random.randint(int(source.base_price * 0.8), int(source.base_price * 1.2))
                error_rate = random.randint(0, 30)
                
                source_product = SourceProduct.objects.create(
                    source=source,
                    product=product,
                    name=f'{product.name} - {source.name}',
                    description=f'Sản phẩm {product.name} từ nguồn {source.name}',
                    product_url=f'https://example.com/product/{product.id}',
                    price=price,
                    error_rate=error_rate
                )
                self.stdout.write(f'Đã tạo liên kết sản phẩm: {source_product.name}')
        
        # Tạo SourceLog
        log_types = ['inquiry', 'purchase', 'warranty']
        admin_user = User.objects.filter(is_staff=True).first()
        
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write('Đã tạo tài khoản admin mặc định')
        
        for source in sources:
            # Tạo logs trong 30 ngày gần đây
            for _ in range(random.randint(5, 15)):
                days_ago = random.randint(0, 30)
                created_at = timezone.now() - timedelta(days=days_ago)
                
                source_products = SourceProduct.objects.filter(source=source)
                source_product = None
                if source_products.exists() and random.random() > 0.3:
                    source_product = random.choice(source_products)
                
                log = SourceLog.objects.create(
                    source=source,
                    source_product=source_product,
                    log_type=random.choice(log_types),
                    has_stock=random.random() > 0.3,  # 70% có hàng
                    processing_time=random.randint(5, 120) if random.random() > 0.2 else None,
                    notes=f'Ghi chú log ngày {created_at.strftime("%d/%m/%Y")}',
                    created_by=admin_user
                )
                
                # Cài đặt thời gian tạo trong quá khứ
                log.created_at = created_at
                log.save()
                
                self.stdout.write(f'Đã tạo log: {log.log_type} cho {source.name}')
        
        self.stdout.write(self.style.SUCCESS('Đã khởi tạo dữ liệu mẫu thành công!')) 