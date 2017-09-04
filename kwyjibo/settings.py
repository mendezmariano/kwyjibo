# -*- coding: utf-8 -*-
"""
Django settings for kwyjibo project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
from .private import *
# SECRET_KEY = '7!o9x^aj=-y4*c3145f&l40@-r%yg8=i($&*p@atzw7dd@f=1u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', 'tps.algoritmos7540mendez.tk']

# Application definition

INSTALLED_APPS = [
    # Application modules
    'teachers.apps.TeachersConfig',
    'students.apps.StudentsConfig',
    'mailing.apps.MailingConfig',
    'revisions.apps.RevisionsConfig',

    # Third-party utilities
    #'bootstrap_toolkit',
    'captcha',
    'kronos',
    'django_nose', ## for coverage

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kwyjibo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'kwyjibo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kwyjibo',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '' 

STATIC_ROOT = '' # os.path.join(BASE_DIR, 'static/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/static/',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)




# URL of the login page.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'



LANGUAGES = (
    ('en', 'English'),
    ('es', 'Español'),
)


###############################################################################
# Particular settings
MAIL_REPLY_ADDRESS    = "support@kwyjibo.org"
MAIL_NO_REPLY_ADDRESS = "no-reply@kwyjibo.org"

# Path customizables
DELIVERY_FILES_PATH = "deliveries/%Y"
ASSIGNMENT_FILES_PATH = "assignments/%Y"
SCRIPT_FILES_PATH = "scripts/%Y"
BROWSE_DELIVERIES_PATH = "browse/"


# Deliveries mime-type
ZIP_MIMETYPE = "application/zip"
ZIP_X_MIMETYPE = "application/x-zip-compressed"
OCTET_STREAM_MIMETYPE = "application/octet-stream"

DELIVERY_ACCEPTED_MIMETYPE = ZIP_MIMETYPE
DELIVERY_ACCEPTED_MIMETYPES = [ZIP_MIMETYPE, ZIP_X_MIMETYPE, OCTET_STREAM_MIMETYPE]
DELIVERY_ACCEPTED_EXTENTION = "zip"

MAX_PAGINATOR_SIZE = 10
