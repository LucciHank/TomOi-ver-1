AUTH_USER_MODEL = 'accounts.CustomUser'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'accounts/static'),
]
LOGIN_URL = '/accounts/login/' 