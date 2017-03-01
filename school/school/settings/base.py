"""
Django settings for school project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from django.core.urlresolvers import reverse_lazy

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!


ALLOWED_HOSTS = ['localhost', '127.0.0.0', '127.0.0.1', '139.59.27.34', 'techassisto.com', 'www.techassisto.com']

CRISPY_TEMPLATE_PACK = 'bootstrap3'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'captcha',
    'school_user',
    'school_genadmin',
    'school_eduadmin',
    'school_classadmin',
    'school_teacher',
    'school_student',
    'school_library',
    'school_account',
    'school_fees',
    'school_salary',
    'school_hr',    
]

AUTH_USER_MODEL='school_user.User'


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'school.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '..', 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'school.wsgi.application'

#This is for django-excel
FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler")


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

#Number grouping to group numbers in a format. Turned off for now.
#NUMBER_GROUPING = (3, 2, 0)

USE_TZ = True

TIME_ZONE = 'Asia/Kolkata'

DATE_INPUT_FORMATS = ('%d-%m-%Y')

USE_I18N = True

USE_L10N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT=os.path.join(BASE_DIR, '..', '..','static','static_school')

STATIC_URL = '/staticschool/'

# Close the session when user closes the browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#Login redirect pages
LOGIN_REDIRECT_URL = reverse_lazy('landing')
LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('logout')

#Security
SECURE_BROWSER_XSS_FILTER=True

#CAPTCHA SETTINGS
NOCAPTCHA = True
RECAPTCHA_USE_SSL = False

#This is where django shall send mail in case of error
ADMINS = (
 ('Sayantan Ganguly', 'sayantan@techassisto.com'),
)

#This is for defining the maximum persistant connection's age (poooling ciinections to DB)
#Its used as creating new pool for postgrres is very expensive
CONN_MAX_AGE = 500