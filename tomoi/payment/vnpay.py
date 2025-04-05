import hashlib
import hmac
import urllib.parse
from datetime import datetime
from django.conf import settings

class VnPay:
    def __init__(self):
        self.vnp_Version = '2.1.0'
        self.vnp_Command = 'pay'
        self.vnp_TmnCode = settings.VNPAY_TMN_CODE
        self.vnp_HashSecret = settings.VNPAY_HASH_SECRET_KEY
        self.vnp_Url = settings.VNPAY_PAYMENT_URL
        self.requestData = {}

    def get_payment_url(self, payment_url, hash_secret, is_deposit=False):
        # Thêm các tham số bắt buộc
        self.requestData['vnp_Version'] = self.vnp_Version
        self.requestData['vnp_Command'] = self.vnp_Command
        self.requestData['vnp_TmnCode'] = self.vnp_TmnCode
        
        # Chọn URL return phù hợp dựa vào loại giao dịch
        if 'vnp_ReturnUrl' not in self.requestData:
            if is_deposit:
                self.requestData['vnp_ReturnUrl'] = settings.VNPAY_DEPOSIT_RETURN_URL
            elif self.requestData.get('vnp_OrderType') == 'order':
                self.requestData['vnp_ReturnUrl'] = settings.VNPAY_ORDER_RETURN_URL
            else:
                self.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            
        # Đảm bảo có ngày tạo nếu chưa có
        if 'vnp_CreateDate' not in self.requestData:
            self.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            
        # Đảm bảo có các trường bắt buộc
        if 'vnp_CurrCode' not in self.requestData:
            self.requestData['vnp_CurrCode'] = 'VND'
        if 'vnp_IpAddr' not in self.requestData:
            self.requestData['vnp_IpAddr'] = '127.0.0.1'
        if 'vnp_Locale' not in self.requestData:
            self.requestData['vnp_Locale'] = 'vn'

        # Sắp xếp các tham số theo thứ tự a-z
        input_data = sorted(self.requestData.items())
        
        # Tạo chuỗi query
        query_string = ''
        seq = 0
        for key, val in input_data:
            if seq == 1:
                query_string = query_string + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                query_string = key + '=' + urllib.parse.quote_plus(str(val))

        # Tạo chữ ký
        hash_value = self._hmacsha512(hash_secret, query_string)
        
        # Trả về URL thanh toán hoàn chỉnh
        return payment_url + "?" + query_string + '&vnp_SecureHash=' + hash_value

    def validate_response(self, response_data):
        vnp_SecureHash = response_data.get('vnp_SecureHash')
        if not vnp_SecureHash:
            return False

        # Remove hash from the validation
        if 'vnp_SecureHash' in response_data:
            response_data.pop('vnp_SecureHash')

        # Sort response data
        input_data = sorted(response_data.items())
        
        # Create query string
        query_string = ''
        seq = 0
        for key, val in input_data:
            if seq == 1:
                query_string = query_string + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                query_string = key + '=' + urllib.parse.quote_plus(str(val))

        # Create secure hash
        hash_value = self._hmacsha512(self.vnp_HashSecret, query_string)
        
        # Compare hashes
        return vnp_SecureHash == hash_value

    def _hmacsha512(self, key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest() 