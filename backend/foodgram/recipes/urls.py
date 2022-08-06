from django.urls import include, path

from rest_framework import routers

from .views import TagViewSet

app_name = 'recipes'

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls))
]
