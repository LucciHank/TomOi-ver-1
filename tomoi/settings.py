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

# Cấu hình VNPAY
VNPAY_TMN_CODE = 'B2RG0YSD'
VNPAY_HASH_SECRET_KEY = 'S500OYUZE6YZRFNMC2LFQZZXMXATAJKK'
VNPAY_PAYMENT_URL = 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'

# URL return cho các giao dịch VNPAY
VNPAY_RETURN_URL = 'https://tomoi.vn/payment/vnpay-return/'
VNPAY_RETURN_URL_DEPOSIT = 'https://tomoi.vn/accounts/deposit/vnpay-deposit-return/'
VNPAY_DEPOSIT_RETURN_URL = 'https://tomoi.vn/accounts/deposit/vnpay-deposit-return/'
VNPAY_ORDER_RETURN_URL = 'https://tomoi.vn/accounts/payment/vnpay-order-return/'
VNPAY_IPN_URL = 'https://tomoi.vn/payment/vnpay-ipn/'

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Các context processor tùy chỉnh
                'store.context_processors.cart_count',
                'store.context_processors.wishlist_count',
                'store.context_processors.categories_list',
                'store.context_processors.unread_messages_count',
            ],
        },
    },
] 