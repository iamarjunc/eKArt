"""
Django settings for ekart project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from decouple import config
from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['.vercel.app','django-env-1.eba-rj2zwr6w.us-west-2.elasticbeanstalk.com','*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'category',
    'accounts',
    'store',
    'cart',
    'orders',
    'admin_honeypot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
]

SESSION_EXPIRE_SECONDS = 160
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = 'login'

ROOT_URLCONF = 'ekart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',
                'cart.context_processors.counter',
            ],
        },
    },
]

WSGI_APPLICATION = 'ekart.wsgi.application'

AUTH_USER_MODEL = 'accounts.Account'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# Database Configuration
# import os
# if 'RDS_DB_NAME' in os.environ:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': os.environ['RDS_DB_NAME'],
#             'USER': os.environ['RDS_USERNAME'],
#             'PASSWORD': os.environ['RDS_PASSWORD'],
#             'HOST': os.environ['RDS_HOSTNAME'],
#             'PORT': os.environ['RDS_PORT'],
#         }
#     }
# else:
#     DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': str(BASE_DIR / 'db.sqlite3'),  # Convert to string
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': str(BASE_DIR / 'db.sqlite3'),  # Convert to string
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': 'davean#123',
#         'HOST': 'database-1.cj8q0k0okx0i.us-east-1.rds.amazonaws.com',
#         'PORT': '5432',
#         'OPTIONS': {
#             'options': '-c timezone=UTC',
#         }
#     }
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': '@rjun#2000',
#         'HOST': 'localhost',  # Set to the PostgreSQL server address if not local
#         'PORT': '5432',       # Default PostgreSQL port
#     }
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres.ugvyttwfumevvwxmbcye',
#         'PASSWORD': 'Davean#123sky',
#         'HOST': 'aws-0-us-east-1.pooler.supabase.com',  # Set to the PostgreSQL server address if not local
#         'PORT': '6543',       # Default PostgreSQL port
#     }
# }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DATABASE_NAME'),
#         'USER': config('DATABASE_USER'),
#         'PASSWORD': config('DATABASE_PASSWORD'),
#         'HOST': config('DATABASE_HOST'),
#         'PORT': config('DATABASE_PORT'),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'SHOPKART',
        'USER':'Sa',
        'PASSWORD':'S@pdb#39',
        'HOST':'ACER\SQLEXPRESS',
        'PORT':'',
        'OPTIONS':{
            'driver':'ODBC Driver 17 for SQL Server',
            'MARS_Connection':True
        }
    }
}
# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR /'static'
STATICFILES_DIRS = [
    'ekart/static',
]

# media files configuration

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR /'media'



MESSAGE_TAGS = {
    messages.ERROR: "danger",
}


# SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'shopkartdemo@gmail.com'  # your email
EMAIL_HOST_PASSWORD = 'eyrv zjzq zpld wzgw'  # your app password

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'