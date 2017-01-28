from .base import *
from .secret import *
from .email import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = distributor_secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

EMAIL_USE_TLS = EMAIL_USE_TLS
EMAIL_HOST = EMAIL_HOST
EMAIL_PORT = EMAIL_PORT
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,                      
        'USER': db_username,
        'PASSWORD': db_password,
        'HOST': 'localhost',   # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',       
    }
}

