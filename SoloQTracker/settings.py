"""
Django settings for SoloQTracker project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", False)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django_rq",
    "django_tables2",
    "django_htmx",
    "crispy_forms",
    "crispy_tailwind",
    "tracker",
    "pyot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "SoloQTracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "SoloQTracker.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# TODO: Move this over to Heroku PGSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# See: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
AUTH_USER_MODEL = "tracker.User"

# pyot
PYOT_CONFS = ["tracker.pyotconf"]

# crispy-forms

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"

# RQ

if config("REDIS", False):
    host = config("REDIS_HOST", False)
    port = config("REDIS_PORT", False)
    db = config("REDIS_DB", False)
    password = config("REDIS_PASSWORD", False)
    if not host or not port or not db or not password:
        raise RuntimeError("Must configure all REDIS env variables.")

    RQ_QUEUES = {
        "default": {
            "HOST": host,
            "PORT": port,
            "DB": db,
            "PASSWORD": password,
            "DEFAULT_TIMEOUT": 360,
        },
        "high": {
            "HOST": host,
            "PORT": port,
            "DB": db,
            "PASSWORD": password,
            "DEFAULT_TIMEOUT": 500,
        },
        "low": {
            "HOST": host,
            "PORT": port,
            "DB": db,
            "PASSWORD": password,
        },
    }
    RQ_SHOW_ADMIN_LINK = True
else:
    raise RuntimeError("Must configure REDIS env variables.")


if config("HEROKU", False):
    import django_on_heroku

    django_on_heroku.settings(locals(), secret_key=False)

    RQ = {
        "JOB_CLASS": "rq.job.Job",
        "WORKER_CLASS": "rq.worker.HerokuWorker",
    }

# sentry
if config("SENTRY", False):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.rq import RqIntegration

    dsn = config("SENTRY_DSN", False)

    if not dsn:
        raise RuntimeError("Looks like you forgot to configure the SENTRY_DSN environment variable.")

    sentry_sdk.init(
        dsn=dsn,
        integrations=[RedisIntegration(), RqIntegration(), DjangoIntegration()],
        # TODO:  Check if 1.0 is viable for production w/small size
        # Make this configurable
        # And also, probably disable PII since I don't use auth.
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

    RQ_SENTRY_DSN = config("RQ_SENTRY_DSN", False)
    if not RQ_SENTRY_DSN:
        RQ_SENTRY_SDN = dsn

if config("DEBUG", False):
    INSTALLED_APPS.append("django_browser_reload")
