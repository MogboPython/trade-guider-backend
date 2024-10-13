import environs

from .dev import *  # noqa: F403

env = environs.Env()

DEBUG = env.bool('DEBUG')

SECRET_KEY = env.str('BACKEND_SECRET_KEY')

DATABASES = {'default': env.dj_db_url('BACKEND_DATABASE_URL')}

CACHES = {'default': env.dj_cache_url('CACHE_URL')}

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.fly.dev']

# CSRF_TRUSTED_ORIGINS = ['https://*.fly.dev']
