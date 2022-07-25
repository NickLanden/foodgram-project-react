from django.urls import include, path
from rest_framework import routers

app_name = 'purchases'

router = routers.DefaultRouter()
router.register(r'recipes/')
