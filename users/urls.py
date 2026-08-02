from rest_framework.permissions import AllowAny

from .views import CustomUserViewSet, PaymentsViewSet, UserCreateAPIView
from rest_framework.routers import DefaultRouter
from .apps import UsersConfig
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'', CustomUserViewSet, basename='users')

router.register(r'payments', PaymentsViewSet, basename='payments')
urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
              ] + router.urls