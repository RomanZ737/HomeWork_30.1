from .views import CustomUserViewSet
from rest_framework.routers import DefaultRouter
from .apps import UsersConfig

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
urlpatterns = [

              ] + router.urls