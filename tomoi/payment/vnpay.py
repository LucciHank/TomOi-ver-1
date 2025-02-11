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
        self.vnp_ReturnUrl = settings.VNPAY_RETURN_URL
        self.requestData = {}

    def get_payment_url(self, payment_url):
        input_data = sorted(self.requestData.items())
        query_string = ''
        seq = 0
        
        for key, val in input_data:
            if seq == 1:
                query_string = query_string + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                query_string = key + '=' + urllib.parse.quote_plus(str(val))

        hash_value = self._hmacsha512(self.vnp_HashSecret, query_string)
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