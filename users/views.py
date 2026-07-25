from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework import viewsets


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
