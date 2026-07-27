from rest_framework import serializers
from .models import CustomUser, Payments




class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    payments = PaymentsSerializer(many=True, read_only=True, source='payments_set')
    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'city', 'payments']