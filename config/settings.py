"""
Django settings for config project.
"""
import environ
import os
from pathlib import Path

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

env.read_env(os.path.join(BASE_DIR, 'config', '.env'))

SECRET_KEY = 'django-insecure-krk)zgyku3_n!f&v-c4-w*nys5bgg*3_r&m&o-$#i@1)egq($7'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'base.apps.BaseConfig',
    'community.apps.CommunityConfig',
    'home.apps.HomeConfig',
    'listings.apps.ListingsConfig',
    'login.apps.LoginConfig',
    'mypage.apps.MypageConfig',
    'recommendations.apps.RecommendationsConfig',
    'django_browser_reload',
    'tailwind',
    'theme',
]
TAILWIND_APP_NAME = 'theme'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ✅ 카카오 로그인 관련 설정 추가
KAKAO_MAP_API_KEY = env("KAKAO_MAP_API_KEY")
KAKAO_REST_API_KEY = env("KAKAO_REST_API_KEY")
KAKAO_REDIRECT_URI = env("KAKAO_REDIRECT_URI")
KAKAO_AUTH_URL = env("KAKAO_AUTH_URL")
KAKAO_TOKEN_URL = env("KAKAO_TOKEN_URL")
KAKAO_USER_INFO_URL = env("KAKAO_USER_INFO_URL")

# Tailwind 설정
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"  # Windows