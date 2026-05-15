"""
ASGI config for vizforge project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vizforge.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # 如果需要WebSocket支持，可以在这里添加WebSocket路由
})
