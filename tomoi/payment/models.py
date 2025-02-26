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
    PAYMENT_METHODS = (
        ('vnpay', 'VNPAY'),
        ('card', 'Thẻ cào'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Chờ xử lý'),
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
    )

    TRANSACTION_TYPES = (
        ('purchase', 'Mua hàng'),
        ('deposit', 'Nạp tiền'),
    )

    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    order = models.ForeignKey('store.Order', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=255, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='purchase')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount}đ - {self.get_status_display()}"

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(null=True, blank=True)
    upgrade_email = models.EmailField(null=True, blank=True)
    account_username = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} - {self.transaction.id}"

    class Meta:
        db_table = 'transaction_items' 