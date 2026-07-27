from .views import CustomUserViewSet, PaymentsViewSet
from rest_framework.routers import DefaultRouter
from .apps import UsersConfig

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'', CustomUserViewSet, basename='users')

router.register(r'payments', PaymentsViewSet, basename='payments')
urlpatterns = [

              ] + router.urls