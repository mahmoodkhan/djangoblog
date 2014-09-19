"""
WSGI config for djangoblog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os, sys
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
ROOT_PATH = os.path.join(PROJECT_PATH, '../')
sys.path.append(ROOT_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoblog.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
