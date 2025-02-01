import json
import hmac
import hashlib
import requests
from datetime import datetime
from django.conf import settings

class InstallmentService:
    def __init__(self):
        self.base_url = "https://sandbox.vnpayment.vn/isp-svc"
        self.client_id = settings.VNPAY_CLIENT_ID
        self.username = settings.VNPAY_USERNAME
        self.password = settings.VNPAY_PASSWORD
        self.client_secret = settings.VNPAY_CLIENT_SECRET
        self.tmn_code = settings.VNPAY_TMN_CODE
        self.secret_key = settings.VNPAY_HASH_SECRET
        self.access_token = None

    def get_access_token(self):
        url = f"{self.base_url}/oauth/authenticate"
        data = {
            "clientId": self.client_id,
            "username": self.username,
            "password": self.password,
            "clientSecret": self.client_secret
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result['rspCode'] == '00':
                self.access_token = result['data']['accessToken']
                return self.access_token
        return None

    def get_installment_info(self, amount):
        if not self.access_token:
            self.get_access_token()
            
        url = f"{self.base_url}/category/get-installment-info"
        
        data = f"{self.tmn_code}|{amount}|VND"
        secure_hash = hmac.new(
            bytes(self.secret_key, 'UTF-8'),
            bytes(data, 'UTF-8'),
            hashlib.sha512
        ).hexdigest()
        
        params = {
            'tmnCode': self.tmn_code,
            'amount': amount,
            'currCode': 'VND',
            'secureHash': secure_hash
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        response = requests.get(url, params=params, headers=headers)
        return response.json()

    def init_installment(self, transaction_data):
        url = f"{self.base_url}/payment/init"
        
        # Tạo checksum cho dữ liệu
        hash_data = self._create_hash_data(transaction_data)
        secure_hash = hmac.new(
            bytes(self.secret_key, 'UTF-8'),
            bytes(hash_data, 'UTF-8'),
            hashlib.sha512
        ).hexdigest()
        
        transaction_data['secureHash'] = secure_hash
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=transaction_data, headers=headers)
        return response.json()

    def _create_hash_data(self, data):
        # Tạo chuỗi hash theo quy tắc của VNPay
        hash_fields = [
            'reqId', 'orderReference', 'orderInfo', 'tmnCode',
            'issuerCode', 'scheme', 'recurringAmount', 'recurringFrequency',
            'recurringNumberOfIsp', 'amount', 'totalIspAmount', 'currCode',
            'addData', 'identityCode', 'forename', 'surname', 'mobile',
            'email', 'address', 'city', 'country', 'ipAddr', 'userAgent',
            'returnUrl', 'cancelUrl', 'version', 'locale', 'mcDate'
        ]
        
        hash_values = []
        for field in hash_fields:
            value = data.get(field, '')
            hash_values.append(str(value))
        
        return '|'.join(hash_values) 