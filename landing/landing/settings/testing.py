#This is only for local use

from .base import *
from .secret import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = landing_secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

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

