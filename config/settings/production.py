from .base import *

DEBUG = False

ALLOWED_HOSTS = ['laporan-medeska.smknj.sch.id', 'www.laporan-medeska.smknj.sch.id']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smkf7622_laporan_harian_medeska',       # Nama database di cPanel
        'USER': 'smkf7622_peaceman',       # Username database di cPanel
        'PASSWORD': 'Bakso@123#123',    # Password user database
        'HOST': 'localhost',               # Tetap localhost karena Django & MySQL berada di server cPanel yang sama
        'PORT': '3306',                    # Port default MySQL
    }
}