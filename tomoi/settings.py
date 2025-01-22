AUTH_USER_MODEL = 'accounts.CustomUser'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'accounts/static'),
]
LOGIN_URL = '/accounts/login/'

MIDDLEWARE = [
    # ... other middleware
    'accounts.middleware.RoleMiddleware',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 