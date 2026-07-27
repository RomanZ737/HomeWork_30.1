from warnings import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import CustomUser, Payments
from .serializers import CustomUserSerializer, PaymentsSerializer
from rest_framework import viewsets


class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('payed_lesson', 'payed_course', 'payment_method')
    ordering_fields = ('payment_at',)
