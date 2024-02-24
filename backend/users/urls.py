from rest_framework import routers
from api.views import ProfileViewSet
from django.urls import include, path
from users.views import create_subscribe


router = routers.DefaultRouter()
router.register(r'users', ProfileViewSet, basename='Users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/<user_id>/subscribe/", create_subscribe),
]