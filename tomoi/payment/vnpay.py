import hmac
import hashlib
from datetime import datetime, timedelta
import urllib.parse

class VNPay:
    requestData = {}
    responseData = {}
    
    def __init__(self):
        self.vnp_TmnCode = "B2RG0YSD"
        self.vnp_HashSecret = "S500OYUZE6YZRFNMC2LFQZZXMXATAJKK"
        self.vnp_Url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
        self.vnp_ReturnUrl = "http://localhost:8000/payment/vnpay-return/"
        
    def get_payment_url(self, amount, order_id, order_desc, bank_code=None):
        # Lấy thời gian hiện tại và thời gian hết hạn
        now = datetime.now()
        expire = now + timedelta(minutes=15)
        
        # Format thời gian theo yêu cầu của VNPay
        vnp_CreateDate = now.strftime('%Y%m%d%H%M%S')
        vnp_ExpireDate = expire.strftime('%Y%m%d%H%M%S')
        
        # Tạo dữ liệu gửi VNPAY
        raw_data = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': self.vnp_TmnCode,
            'vnp_Amount': int(amount * 100),
            'vnp_CreateDate': vnp_CreateDate,
            'vnp_CurrCode': 'VND',
            'vnp_IpAddr': '127.0.0.1',
            'vnp_Locale': 'vn',
            'vnp_OrderInfo': order_desc,
            'vnp_OrderType': 'other',
            'vnp_ReturnUrl': self.vnp_ReturnUrl,
            'vnp_TxnRef': order_id,
            'vnp_ExpireDate': vnp_ExpireDate
        }
        
        if bank_code:
            raw_data['vnp_BankCode'] = bank_code

        # Sắp xếp theo key và mã hóa URL các giá trị
        sorted_items = sorted(raw_data.items())
        hash_data = ''
        seq = 0
        for key, value in sorted_items:
            if seq == 1:
                hash_data = hash_data + "&" + urllib.parse.quote_plus(str(key)) + "=" + urllib.parse.quote_plus(str(value))
            else:
                hash_data = urllib.parse.quote_plus(str(key)) + "=" + urllib.parse.quote_plus(str(value))
                seq = 1

        # Tạo chữ ký
        secure_hash = hmac.new(
            bytes(self.vnp_HashSecret, 'UTF-8'),
            bytes(hash_data, 'UTF-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Thêm chữ ký vào data
        raw_data['vnp_SecureHash'] = secure_hash
        
        # Tạo URL thanh toán với các tham số được mã hóa
        query_string = ''
        seq = 0
        for key, value in sorted_items:
            if seq == 1:
                query_string = query_string + "&" + urllib.parse.quote_plus(str(key)) + "=" + urllib.parse.quote_plus(str(value))
            else:
                query_string = urllib.parse.quote_plus(str(key)) + "=" + urllib.parse.quote_plus(str(value))
                seq = 1

        query_string += f"&vnp_SecureHash={secure_hash}"
        return f"{self.vnp_Url}?{query_string}" 