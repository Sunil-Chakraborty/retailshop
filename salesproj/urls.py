from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('sales/', include('sales.urls', namespace='sales')),  # Default route for sales app
    path('seller/', include('seller_app.urls', namespace='seller_app')),  # Prefix 'seller/' for seller_app routes
]

if settings.DEBUG:  # Serve static and media files in debug mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
