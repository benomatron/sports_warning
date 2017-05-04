import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.abspath(os.path.dirname(__file__)) + '/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_nose',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'whitenoise.runserver_nostatic',
    'smsish',
    'sportswar.events',
    'sportswar.teams',
    'sportswar.users',
]

SITE_URL = 'http://127.0.0.1'
LOGIN_URL = 'http://127.0.0.1/login'
LOGIN_REDIRECT_URL = 'http://127.0.0.1/watchers'
DOMAIN = '127.0.0.1'
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@sportswarning.com'
SERVER_EMAIL = 'server@sportswarning.com'
EMAIL_HOST = 'localhost'
SITE_ID = 1

# uncomment for https
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

##############################################
# Settings that should be configured in local_settings
# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", None)
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", None)
# TWILIO_MAGIC_FROM_NUMBER = "+15005550006"  # This number passes all validation.
# TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", TWILIO_MAGIC_FROM_NUMBER)

# SMS_BACKEND_CONSOLE = 'smsish.sms.backends.console.SMSBackend'
# SMS_BACKEND_DUMMY = 'smsish.sms.backends.dummy.SMSBackend'
# SMS_BACKEND_TWILIO = 'smsish.sms.backends.twilio.SMSBackend'
# SMS_BACKEND = SMS_BACKEND_CONSOLE

# AUTHY_KEY = 'blahblahblah'
# AUTHY_IS_SANDBOXED = False

# DATABASES = { all the database stuff}

# SEATGEEK_CLIENT_ID = 'xxxxxxxxxxxxxxx'
# SEATGEEK_SECRET = 'xxxxxxxxxxxxxx'
##############################################

# from django rest_auth and all_auth setup
# ACCOUNT_LOGOUT_ON_GET = True

# uncomment in prod
# ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = LOGIN_REDIRECT_URL
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300

OLD_PASSWORD_FIELD_ENABLED = True

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sportswar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'sportswar.wsgi.application'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# TEST_RUNNER = 'django.test.runner.DiscoverRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=sportswar',
    '--cover-html',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'sportswar.users.serializers.CustomRegisterSerializer',
}

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbname',
        'USER': 'dbuser',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

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

# CELERY STUFF
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

NODE_MODULES_ROOT = os.path.join(PACKAGE_DIR, '../node_modules')
STATICFILES_DIRS = (os.path.join(PACKAGE_DIR, '../assets'), )
STATIC_ROOT = os.path.join(PACKAGE_DIR, '../static')
STATIC_URL = '/static/'

# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base': {
            'format': '%(asctime)s %(levelname)s %(name)s %(pathname)s:%(lineno)d'
                      ' %(funcName)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'base'
        },
        'email-admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': False,
        },
    },
    'loggers': {
        'sportswar': {
            'handlers': ['console', 'email-admins'],
            'propagate': True,
            'level': 'INFO'
        },
        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO'
        },
        'django.request': {
            'handlers': ['console', 'email-admins'],
            'propagate': False,
            'level': 'WARNING'
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'WARNING'
        },
        'celery': {
            'handlers': ['console', 'email-admins'],
            'propagate': True,
            'level': 'INFO'
        },
        'celery.task': {
            'handlers': ['console', 'email-admins'],
            'propagate': False,
            'level': 'INFO'
        },
        'gunicorn': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO'
        },
    }
}

try:
    from sportswar.local_settings import *  # pylint: disable=wildcard-import
except ImportError:
    print('Could not import local settings')
