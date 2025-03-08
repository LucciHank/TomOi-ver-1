DEBUG = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.EmailVerificationMiddleware',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'accounts/static'),
    # ... other static directories
]

# Cấu hình DoiThe.vn API
DOITHE_PARTNER_ID = 'your_partner_id'
DOITHE_PARTNER_KEY = 'your_partner_key'
DOITHE_API_URL = 'https://doithe.vn/api/card-auto'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'accounts',
    'dashboard',
    'store',
    'blog',
    # Các app khác...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Nếu có AUTHENTICATION_BACKENDS, hãy đảm bảo không có social_django
# Ví dụ: SOCIAL_AUTH_FACEBOOK_KEY, SOCIAL_AUTH_FACEBOOK_SECRET, v.v. 

# Thêm cài đặt này để tắt cảnh báo về template tag trùng tên
SILENCED_SYSTEM_CHECKS = ['templates.W003'] 

# Thêm vào cuối file settings.py
GOOGLE_OAUTH2_CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, 'client_secret.json')
# Cấu hình cho Google OAuth
OAUTHLIB_INSECURE_TRANSPORT = DEBUG  # Cho phép HTTP trong môi trường dev
OAUTHLIB_RELAX_TOKEN_SCOPE = True 