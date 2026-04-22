from .settings import *

# Local MongoDB override (localhost:27017)
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'agnayi_crm',
        'CLIENT': {
            'host': 'localhost',
            'port': 27017,
            'username': '',
            'password': '',
        }
    }
}

DEBUG = True
SECRET_KEY = 'django-insecure-local-testing-change-in-production'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

