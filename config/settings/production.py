from .base import *

DEBUG = False

ALLOWED_HOSTS = ['domainanda.com', 'www.domainanda.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}