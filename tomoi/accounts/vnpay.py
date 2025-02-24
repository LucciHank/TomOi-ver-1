import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any
from urllib.parse import urlencode
from django.conf import settings

class VNPay:
    def __init__(self):
        self.requestData = {}
        self.responseData = {}

    def get_payment_url(self, vnpay_payment_url: str, secret_key: str, is_deposit: bool = True) -> str:
        """Tạo URL thanh toán VNPay"""
        # Thêm thời gian hết hạn thanh toán (15 phút)
        expire_date = datetime.now() + timedelta(minutes=15)
        self.requestData['vnp_ExpireDate'] = expire_date.strftime('%Y%m%d%H%M%S')

        # Thêm return URL tương ứng
        if is_deposit:
            self.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL_DEPOSIT
        else:
            self.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL_ORDER

        # Sắp xếp các tham số theo thứ tự a-z
        sorted_items = sorted(self.requestData.items())

        # Tạo chuỗi hash data
        hash_data = ""
        i = 0
        for key, val in sorted_items:
            if val in ["", None]:  # Bỏ qua tham số rỗng
                continue
            
            if i == 1:
                hash_data += '&' + urlencode({key: str(val).strip()})
            else:
                hash_data += urlencode({key: str(val).strip()})
                i = 1

        # Tạo HMAC-SHA512
        secure_hash = hmac.new(
            bytes(secret_key, 'utf-8'),
            bytes(hash_data, 'utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Tạo query string
        query_string = hash_data + f"&vnp_SecureHash={secure_hash}"

        # Debug log
        print("Hash Data:", hash_data)
        print("Secure Hash:", secure_hash)
        print("Query String:", query_string)

        return f"{vnpay_payment_url}?{query_string}"

    def validate_response(self, secret_key: str) -> bool:
        """Xác thực response từ VNPay"""
        if not self.responseData:
            return False

        # Lấy secure hash từ response
        vnp_secure_hash = self.responseData.pop('vnp_SecureHash', '')
        
        # Sắp xếp các tham số theo thứ tự a-z
        sorted_items = sorted(self.responseData.items())
        
        # Tạo chuỗi hash data
        hash_data = ""
        i = 0
        for key, val in sorted_items:
            if val in ["", None]:  # Bỏ qua tham số rỗng
                continue
            
            # Chuyển giá trị thành string và loại bỏ khoảng trắng đầu/cuối
            str_val = str(val).strip()
            
            if i == 1:
                hash_data += '&' + urlencode({key: str_val})
            else:
                hash_data += urlencode({key: str_val})
                i = 1

        # Tạo secure hash để so sánh
        secure_hash = hmac.new(
            bytes(secret_key, 'utf-8'),
            bytes(hash_data, 'utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Debug log
        print("Response Hash Data:", hash_data)
        print("Response Secure Hash:", secure_hash)
        print("VNPay Secure Hash:", vnp_secure_hash)

        # So sánh 2 chuỗi secure hash
        return vnp_secure_hash == secure_hash 