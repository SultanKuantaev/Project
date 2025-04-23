# shop_backend/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include the URLs from your API app, prefixing them with 'api/'
    path('api/', include('api.urls')),
]