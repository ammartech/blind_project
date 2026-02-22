from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-saqccwpKPqVMgGD2o7FqB6LeZkqOt7bY3KKYP0OmIy9nRXnB'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'core',
    'service',
    'glossary',
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

ROOT_URLCONF = 'taibah_voice.urls'

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

WSGI_APPLICATION = 'taibah_voice.wsgi.application'

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

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'service:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

# A simple flag you can toggle later to integrate real speech-to-text and text-to-speech providers
VOICE_PIPELINE_MODE = 'demo'  # demo | provider

# ==============================================
# TTS Settings - Add to your taibah_voice/settings.py
# ==============================================

# TTS Configuration
import os

# Directory for cached TTS audio files
TTS_OUTPUT_DIR = os.path.join(MEDIA_ROOT, 'tts_audio')

# Directory for voice sample files (male_arabic.wav, female_arabic.wav)
TTS_VOICES_DIR = os.path.join(BASE_DIR, 'service', 'tts_voices')


# ==============================================
# Installation Instructions
# ==============================================
"""
1. Install dependencies:
   pip install TTS torch torchaudio soundfile

2. Copy service files:
   - service/views.py (updated with TTS views)
   - service/urls.py (updated with TTS URLs)
   - service/tts_service.py (new file)

3. Copy static files:
   - static/js/tts.js (new file)
   - Append static/css/tts_styles.css to your main.css

4. Create voice samples directory:
   mkdir -p service/tts_voices

5. Add voice samples (6+ seconds WAV files):
   - service/tts_voices/male_arabic.wav
   - service/tts_voices/female_arabic.wav

6. Add TTS settings to settings.py (above)

7. Create media directory:
   mkdir -p media/tts_audio

8. First run will download XTTS-v2 model (~1.8GB)
"""
