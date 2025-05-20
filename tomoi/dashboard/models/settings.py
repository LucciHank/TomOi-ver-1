from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class GeneralSettings(models.Model):
    """Cài đặt hệ thống chung và các cấu hình thanh toán"""
    # Thông tin website
    site_name = models.CharField(max_length=100, default="TomOi", verbose_name=_("Tên website"))
    site_description = models.TextField(blank=True, verbose_name=_("Mô tả website"))
    site_url = models.URLField(verbose_name=_("URL website"), default="https://tomoi.vn")
    contact_email = models.EmailField(default="contact@tomoi.vn", verbose_name=_("Email liên hệ"))
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Số điện thoại"))
    address = models.TextField(blank=True, verbose_name=_("Địa chỉ"))
    
    # Logo và favicon
    logo = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_("Logo"))
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_("Favicon"))
    
    # Mạng xã hội
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    twitter_url = models.URLField(blank=True, verbose_name=_("Twitter URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))
    youtube_url = models.URLField(blank=True, verbose_name=_("YouTube URL"))
    
    # Cấu hình thanh toán VNPay
    vnpay_merchant_id = models.CharField(max_length=100, blank=True, verbose_name=_("VNPay Merchant ID"))
    vnpay_hash_secret = models.CharField(max_length=100, blank=True, verbose_name=_("VNPay Hash Secret"))
    vnpay_api_url = models.URLField(blank=True, default="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html", 
                                  verbose_name=_("VNPay API URL"))
    
    # Cấu hình thanh toán ACB
    acb_merchant_id = models.CharField(max_length=100, blank=True, verbose_name=_("ACB Merchant ID"))
    acb_secret_key = models.CharField(max_length=100, blank=True, verbose_name=_("ACB Secret Key"))
    acb_api_url = models.URLField(blank=True, default="https://sandbox.acbpay.vn/api", 
                                verbose_name=_("ACB API URL"))
    
    # Cấu hình thanh toán PayPal
    paypal_client_id = models.CharField(max_length=100, blank=True, verbose_name=_("PayPal Client ID"))
    paypal_client_secret = models.CharField(max_length=100, blank=True, verbose_name=_("PayPal Client Secret"))
    paypal_mode = models.CharField(max_length=10, default="sandbox", choices=[
        ('sandbox', 'Sandbox'),
        ('live', 'Live')
    ], verbose_name=_("PayPal Mode"))
    
    # Cấu hình SMTP
    smtp_host = models.CharField(max_length=100, blank=True, verbose_name=_("SMTP Host"))
    smtp_port = models.IntegerField(default=587, verbose_name=_("SMTP Port"))
    smtp_username = models.CharField(max_length=100, blank=True, verbose_name=_("SMTP Username"))
    smtp_password = models.CharField(max_length=100, blank=True, verbose_name=_("SMTP Password"))
    smtp_use_tls = models.BooleanField(default=True, verbose_name=_("Sử dụng TLS"))
    default_from_email = models.EmailField(blank=True, verbose_name=_("Email gửi mặc định"))
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Ngày tạo"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Ngày cập nhật"))
    
    class Meta:
        verbose_name = _("Cài đặt hệ thống")
        verbose_name_plural = _("Cài đặt hệ thống")
    
    def __str__(self):
        return f"Cài đặt hệ thống - {self.site_name}"
    
    def save(self, *args, **kwargs):
        # Chỉ cho phép một bản ghi cài đặt duy nhất
        if GeneralSettings.objects.exists() and not self.pk:
            # Cập nhật bản ghi hiện có thay vì tạo mới
            existing = GeneralSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """Lấy hoặc tạo các cài đặt hệ thống"""
        try:
            return cls.objects.first()
        except cls.DoesNotExist:
            return cls.objects.create() 
 
 