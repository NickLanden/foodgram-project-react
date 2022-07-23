from django.contrib import admin
from django.urls import include, path

from users.views import UserViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
]
