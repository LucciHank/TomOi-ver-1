DEBUG = True

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    ...
    'accounts.middleware.EmailVerificationMiddleware',
    ...
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