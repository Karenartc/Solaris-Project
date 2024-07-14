import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR es la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ADVERTENCIA DE SEGURIDAD: Mantén la clave secreta en secreto en producción
SECRET_KEY = 'django-insecure-l08$e0^ot*w(9=bcs!#tlj+hlyg+81#sp36cvd-q)h%@@s5bp)'

# ADVERTENCIA DE SEGURIDAD: No ejecutes con debug activado en producción
DEBUG = True

# Lista de hosts permitidos para este sitio
ALLOWED_HOSTS = []

# Definición de aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin', # Admin de Django
    'django.contrib.auth', # Sistema de autenticación de Django
    'django.contrib.contenttypes', # Tipos de contenido de Django
    'django.contrib.sessions', # Gestión de sesiones
    'django.contrib.messages', # Sistema de mensajes
    'django.contrib.staticfiles', # Archivos estáticos
    'solaris_app', # Aplicación personalizada solaris_app
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # Seguridad
    'django.contrib.sessions.middleware.SessionMiddleware', # Gestión de sesiones
    'django.middleware.common.CommonMiddleware', # Middleware común
    'django.middleware.csrf.CsrfViewMiddleware', # Protección CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Autenticación
    'django.contrib.messages.middleware.MessageMiddleware', # Mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Protección clickjacking
]

ROOT_URLCONF = 'Solaris_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'Solaris_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

#Aquí se configura la conexión a la base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'you_db_name',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'solaris_app.User'

# Configuración para enviar correos electrónicos
# Aquí se configura el servidor de correo electrónico
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email'
EMAIL_HOST_PASSWORD = 'your_password'
DEFAULT_FROM_EMAIL = 'your_email'
