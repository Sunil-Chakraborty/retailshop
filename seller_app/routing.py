from django.urls import re_path
from .consumers import SellerNotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", SellerNotificationConsumer.as_asgi()),
]
