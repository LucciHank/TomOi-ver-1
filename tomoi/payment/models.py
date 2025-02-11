from django.db import models
from django.conf import settings
import random
from datetime import datetime
from django.core.validators import MinValueValidator

class InstallmentTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_reference = models.CharField(max_length=100, unique=True)
    order_info = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    recurring_amount = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_installments = models.IntegerField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    issuer_code = models.CharField(max_length=20)  # Mã ngân hàng
    scheme = models.CharField(max_length=20)  # VISA/JCB/MASTERCARD
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    vnpay_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'installment_transactions'

class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('vnpay', 'VNPAY'),
        ('tcoin', 'TCoin'),
        ('momo', 'MoMo'),
        ('paypal', 'PayPal')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('processing', 'Chờ xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Lỗi'),
        ('cancelled', 'Huỷ')
    ]

    TRANSACTION_TYPES = [
        ('purchase', 'Mua hàng'),
        ('deposit', 'Nạp tiền')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Lấy số cuối cùng từ transaction_id gần nhất
            last_transaction = Transaction.objects.order_by('-transaction_id').first()
            if last_transaction and len(last_transaction.transaction_id) >= 12:
                last_number = int(last_transaction.transaction_id[5:11])
                next_number = str(last_number + 1).zfill(6)
            else:
                next_number = '012345'

            # Tạo transaction_id mới
            now = datetime.now()
            self.transaction_id = f"T{now.strftime('%y%m')}{next_number}{now.strftime('%d')}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount}đ"

    class Meta:
        ordering = ['-created_at']

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    upgrade_email = models.EmailField(null=True, blank=True)
    account_username = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'transaction_items' 