"""
Django settings for law project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
# from decouple import Config, Csv
from decouple import config
import dj_database_url



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*%jad^o4gud+9b)_&fkm&n)z4jd&$^758boq7nd6tw7yy+xlna'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'taggit',
    'widget_tweaks',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.RedirectAuthenticatedUserMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'law.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'accounts/templates')],        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'law.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
        
#     }
# }


import dj_database_url
import os

# Assuming DATABASE_URL is properly set in your environment variables

DATABASE_URL = os.getenv('postgres://advocateassist_user:fl8ejh9cTY8skwMcQBifgPMNKHuZZzLg@dpg-co2kehkf7o1s73ckg95g-a.oregon-postgres.render.com/advocateassist')
DATABASES = {
    'default': dj_database_url.config(),
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

# AUTHENTICATION_BACKENDS = [
#     'django.contrib.auth.backends.ModelBackend',  
#]

AUTHENTICATION_BACKENDS = [
    'accounts.auth_backends.EmailBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'accounts.auth_backends.PhoneBackend',
]

# law/settings.py

LOGIN_URL = 'login'  # Redirect to login view if authentication is required
LOGOUT_REDIRECT_URL = 'login'  # Redirect to login view after logout

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
# EMAIL_HOST_USER = '0aa1c5dd9bd02a'
# EMAIL_HOST_PASSWORD = '2f6f4690adbf1a'
# EMAIL_PORT = '2525'


# config = Config()

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='edxfr3q@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='rfzkspjabfuqofbh')

STATIC_URL = 'static/'
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'FIELDS': ['id', 'email'],
        'APP': {
            'client_id': '803911158543-8o1lh058ran1bs20qbsmfo9i096gsbuc.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        }
    }
}
SOCIALACCOUNT_LOGIN_ON_GET=True


MEDIA_URL = ''
MEDIA_ROOT = os.path.join(BASE_DIR, '')

SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True


RAZORPAY_KEY_ID = "rzp_test_HvhhTnPiTU4aMn"
RAZORPAY_KEY_SECRET = "cTLjyyGZiJD5Ov7neabYmKZK"

TWILIO_PHONE_NUMBER = '+447360273978'

TWILIO_AUTH_TOKEN = '8b00ba49e9d7a6ba60c0890e70f38e1c'

TWILIO_ACCOUNT_SID = 'AC1a93b168e58f46323a25cdbd950ba26f'


# ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'


CORS_ORIGIN_WHITELIST = [
    'https://api.razorpay.com',
]

CSRF_TRUSTED_ORIGINS = ["https://api.razorpay.com","https://5ea1-103-159-151-86.ngrok-free.app"]






