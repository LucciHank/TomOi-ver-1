import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SePayService:
    def __init__(self):
        self.api_key = settings.SEPAY_API_KEY
        self.base_url = 'https://api.sepay.vn/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def check_transaction(self, order_id, amount):
        try:
            url = f"{self.base_url}/transactions"
            params = {
                'reference': f"DH{order_id}",
                'amount': amount
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"SePay transaction check response: {data}")
            
            if data.get('status') == 'success':
                transactions = data.get('data', [])
                # Kiểm tra xem có giao dịch nào khớp với số tiền và mã đơn hàng không
                for transaction in transactions:
                    if (transaction.get('amount') == amount and 
                        transaction.get('status') == 'completed'):
                        return True, transaction.get('id')
            
            return False, None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking SePay transaction: {str(e)}")
            return False, None 