from .base import *
from .secret import *
from .email import *

SECRET_KEY = school_secret_key

DEBUG = False

EMAIL_USE_TLS = EMAIL_USE_TLS
EMAIL_HOST = EMAIL_HOST
EMAIL_PORT = EMAIL_PORT
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL

RECAPTCHA_PUBLIC_KEY = RECAPTCHA_PUBLIC_KEY
RECAPTCHA_PRIVATE_KEY = RECAPTCHA_PRIVATE_KEY


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,                      
        'USER': db_username,
        'PASSWORD': db_password,
        'HOST': 'localhost',  
        'PORT': '',       
    }
}


#For the hash function to work
SALT=SALT