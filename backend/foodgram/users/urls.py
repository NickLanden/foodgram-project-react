from django.urls import include, path
from djoser.views import TokenDestroyView
from rest_framework import routers

from .views import TokenCreateView, UserViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path('', include(router.urls)),
]
