from django.urls import include, path
from rest_framework import routers

from views import RecipeViewSet

app_name = 'recipes'

router_v1 = routers.DefaultRouter()
router_v1.register(
    r'recipes',
    RecipeViewSet,
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
