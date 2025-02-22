import requests
import user_agents
import hashlib
import hmac
import urllib.parse
from django.conf import settings
from datetime import datetime

def mask_email(email):
    """
    Mask email address:
    hoanganhdo182@gmail.com → h****2@gmail.com
    """
    if not email or '@' not in email:
        return email
        
    local_part, domain = email.split('@')
    
    if len(local_part) <= 2:
        return f"{local_part}@{domain}"
        
    masked = f"{local_part[0]}{'*' * (len(local_part)-2)}{local_part[-1]}@{domain}"
    return masked 

def get_client_info(request):
    """Lấy thông tin thiết bị và trình duyệt"""
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = user_agents.parse(ua_string)
    
    # Xác định thiết bị
    if user_agent.is_mobile:
        device = "Mobile Device"
        if user_agent.is_tablet:
            device = "Tablet"
    elif user_agent.is_pc:
        device = "Desktop/Laptop"
    else:
        device = "Unknown Device"
            
    # Xác định trình duyệt và phiên bản
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    
    return device, browser

def get_location_from_ip(ip):
    """
    Lấy thông tin vị trí từ địa chỉ IP sử dụng ipapi.co
    """
    try:
        if not ip or ip == '127.0.0.1' or ip.startswith('192.168.'):
            return 'Local Network'
            
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', '')
            country = data.get('country_name', '')
            if city and country:
                return f"{city}, {country}"
            elif country:
                return country
            else:
                return 'Unknown'
    except:
        return 'Unknown' 

def create_vnpay_url(deposit):
    vnp_Params = {}
    vnp_Params['vnp_Version'] = '2.1.0'
    vnp_Params['vnp_Command'] = 'pay'
    vnp_Params['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
    vnp_Params['vnp_Amount'] = int(deposit.amount) * 100
    vnp_Params['vnp_CurrCode'] = 'VND'
    vnp_Params['vnp_TxnRef'] = deposit.transaction_id
    vnp_Params['vnp_OrderInfo'] = f'Nap tien tai khoan {deposit.user.username}'
    vnp_Params['vnp_OrderType'] = 'billpayment'
    vnp_Params['vnp_Locale'] = 'vn'
    vnp_Params['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
    vnp_Params['vnp_IpAddr'] = '127.0.0.1'
    vnp_Params['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')

    vnp_Params = sorted(vnp_Params.items())
    hash_data = '&'.join([f'{k}={v}' for k, v in vnp_Params])
    
    secret = bytes(settings.VNPAY_HASH_SECRET_KEY, 'utf-8')
    hash = hmac.new(secret, bytes(hash_data, 'utf-8'), hashlib.sha512).hexdigest()
    
    vnp_Params.append(('vnp_SecureHash', hash))
    vnpay_payment_url = settings.VNPAY_PAYMENT_URL + "?" + urllib.parse.urlencode(vnp_Params)
    
    return vnpay_payment_url

def process_card_payment(card_info):
    data = {
        'partner_id': settings.DOITHE_PARTNER_ID,
        'request_id': card_info['transaction_id'],
        'telco': card_info['telco'],
        'amount': card_info['amount'],
        'serial': card_info['serial'],
        'code': card_info['pin'],
        'command': 'charging'
    }
    
    # Tạo chữ ký
    sign_string = '|'.join([
        settings.DOITHE_PARTNER_ID,
        data['request_id'],
        data['telco'],
        str(data['amount']),
        data['serial'],
        data['code'],
        settings.DOITHE_PARTNER_KEY
    ])
    
    data['sign'] = hashlib.md5(sign_string.encode()).hexdigest()
    
    response = requests.post(settings.DOITHE_API_URL, json=data)
    return response.json() 