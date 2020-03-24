"""
Django settings for ytwebserver project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import platform
from . import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y37#@!rb((7_j03uj=-p%268clc+(-da0d%i$(sf=0rm79y#k='

# SECURITY WARNING: don't run with debug turned on in production!
if platform.system() == 'Windows':  # 测试环境
    DEBUG = True
elif platform.system() == 'Linux':  # 生产环境
    DEBUG = False
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    # 系统自带app
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方app
    # 富文本编辑
    'ckeditor',
    'ckeditor_uploader',
    # 搜索引擎
    'haystack',
    
    # 自己的app
    'andon',
    'technology_lesson_learned',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ytwebserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'ytwebserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ytwebserver',
        'USER': 'ytwebserver',
        'PASSWORD': config.DATABASE_PASSWORD_default,
        'HOST': config.HOST_default,
        'PORT': '5432',
    },
}

# 多数据库自动路由设置
# 设置数据库的路由规则
# Project: 建立的django项目名称(project_name)
# database_router: 定义路由规则database_router.py 文件名称, 这个文件名可以自己定义
# DatabaseAppsRouter: 路由规则的类名称，这个类是在database_router.py 文件中定义
DATABASE_ROUTERS = ['ytwebserver.database_router.DatabaseAppsRouter']


# 设置APP对应的数据库路由表
DATABASE_APPS_MAPPING = {
    # example:
    # 'app_name':'database_name',
    # 系统自带app

    # 第三方app

    # 自己的app
    #'andon': 'default'
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

#USE_TZ = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
# 收集的django静态文件存放位置
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
# 这个是设置静态文件夹目录的路径
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

############################################################################################################
# 设置文件上传路径，图片上传、文件上传都会存放在此目录里
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CKEDITOR_UPLOAD_PATH = 'upload/'
CKEDITOR_CONFIGS = {
    'default': {},
    'comment_ckeditor': {
        'toolbar': 'custom',
        'toolbar_custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript'],
            ['TextColor', 'BGColor', 'RemoveFormat'],
            ['NumberedList', 'BulletedList'],
            ['Smiley', 'SpecialChar', 'Blockquote'],
        ],
        'width': 'auto',
        'height': '180',
        'tabSpaces': 4,
        'removePlugins': 'elementspath',
        'resize_enabled': False,
    }
}

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}


# 发送邮件设置
# https://docs.djangoproject.com/en/2.2/ref/settings/#email
# https://docs.djangoproject.com/en/2.2/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = 25
EMAIL_HOST_USER = config.EMAIL_HOST_USER
# EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_SUBJECT_PREFIX = ['ytwebserver_error']
# EMAIL_USE_SSL = True


# Each item in the list should be a tuple of (Full name, email address). Example:
# [('John', 'john@example.com'), ('Mary', 'mary@example.com')]
ADMINS = config.ADMINS
# 日志文件
# https://docs.djangoproject.com/en/2.2/topics/logging/
if platform.system() == 'Windows':
    pass
elif platform.system() == 'Linux':
    LOGGING = {
        'version': 1,  # 日志版本，可以自己定义
        'disable_existing_loggers': False,  # 是否禁用已经存在的（Django自己的）日志文件记录器
        'handlers': {  # 定义
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                # 日志文件要记录到什么地方，建议不要放在项目里，日志文件会自动增长，不便于Github操作
                # 另外要注意，要修改文件的读写权限为所有人可读写，chmod 666 ytwebserver_debug.log
                'filename': '/home/ytadmin/program/ytwebserver_debug.log',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                # 'filters': ['special']  # 筛选器，这里不需要：只要报错就发送邮件给管理员邮箱
            }
        },
        'loggers': {  # 记录器
            'django': {
                'handlers': ['file'],  # 记录哪个文件，这里选择的是上面定义的'file'
                'level': 'DEBUG',  # 记录级别，>= DEBUG  级别定义：debug<info<warning<error<critical
                'propagate': True,  # 错误是否向上一级别传递
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
        },
    }


# 全局变量
EACH_PAGE_NUMBER = 5  # 分页用的，每页包含几条数据

# 添加搜索引擎
HAYSTACK_CONNECTIONS = {
    'default': {
        # 指定使用的搜索引擎
        'ENGINE': 'haystack.backends.whoosh_cn_backend.WhooshEngine',
        # 指定索引文件存放位置
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}

# 新增的数据自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5