import requests
import user_agents

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