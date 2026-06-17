import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ajoute le répertoire des apps au Python path
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Charge les variables d'environnement depuis un fichier .env (si présent)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass


def env_bool(name, default='False'):
    """Lit une variable d'environnement booléenne (True/1/yes/on)."""
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


# ============================================================
# SÉCURITÉ — valeurs lues depuis l'environnement en production
# ============================================================

# Clé secrète : DOIT être fournie via DJANGO_SECRET_KEY en production.
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dq_#7#^r3f&1@@uaobg5=kdmcso1i-h!!7j!3gy2#gora-e6ja'
)

# DEBUG=True par défaut (dev local). Mettre DJANGO_DEBUG=False en production.
DEBUG = env_bool('DJANGO_DEBUG', 'True')

# Hôtes autorisés (liste séparée par des virgules). '*' uniquement en dev.
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if h.strip()]

# Origines de confiance CSRF (obligatoire en HTTPS avec Django 4.0+).
# Ex : DJANGO_CSRF_TRUSTED_ORIGINS=https://academiq.mondomaine.fr
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps projet
    'core',
    'accounts',
    'personnel',
    'enseignant',
    'eleve',
    'parent',
    # Formulaires Bootstrap
    'crispy_forms',
    'crispy_bootstrap5',
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

ROOT_URLCONF = 'academiq.urls'

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
                'core.context_processors.notifications_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'academiq.wsgi.application'

# ============================================================
# BASE DE DONNÉES
#   - Par défaut  : SQLite (développement local)
#   - Production  : MySQL/MariaDB si DB_ENGINE=mysql
# ============================================================
if os.environ.get('DB_ENGINE', 'sqlite') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', ''),
            'USER': os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'core.Personne'

# Hachage des mots de passe
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# Redirection login/logout
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ============================================================
# FICHIERS STATIQUES & MÉDIAS
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'      # cible de `collectstatic` (production)
STATICFILES_DIRS = [BASE_DIR / 'static']     # sources de développement

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# WhiteNoise : sert et compresse les fichiers statiques en production.
# Activé automatiquement si le paquet est installé (sans casser le dev local).
try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STORAGES['staticfiles']['BACKEND'] = 'whitenoise.storage.CompressedStaticFilesStorage'
except ImportError:
    pass

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ============================================================
# RÉGLAGES DE SÉCURITÉ — actifs uniquement en production (DEBUG=False)
# ============================================================
if not DEBUG:
    # Derrière le proxy SSL d'O2Switch (Apache + Passenger)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    # Redirection HTTPS : passer DJANGO_SSL_REDIRECT=True une fois le certificat SSL actif.
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SSL_REDIRECT', 'False')
