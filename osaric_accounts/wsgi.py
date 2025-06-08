"""
WSGI config for osaric_accounts project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use Railway settings if deployed on Railway, otherwise use default settings
if os.environ.get('RAILWAY_ENVIRONMENT'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osaric_accounts.settings_railway')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osaric_accounts.settings')

application = get_wsgi_application()
