"""
ASGI config for nexalink project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexalink.settings')

application = get_asgi_application()
