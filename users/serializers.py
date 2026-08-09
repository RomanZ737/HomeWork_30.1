from rest_framework import serializers
from .models import CustomUser, Payments
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError



class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = ['id', 'payed_course', 'payed_lesson',
                  'payment_amount', 'payment_method', 'payment_link',
                  'stripe_session_id', 'payment_status', 'payment_at']
        read_only_fields = ['id', 'payment_link', 'stripe_session_id', 'payment_status', 'payment_at']


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=2)
    payments = PaymentsSerializer(many=True, read_only=True, source='payments_set')

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'city', 'payments', 'password']


    def to_representation(self, instance):
        request = self.context.get('request')

        if request and request.user == instance:
            return super().to_representation(instance)

        return {
            'id': instance.id,
            'email': instance.email,
            'phone_number': instance.phone_number,
            'city': instance.city,
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')

        try:
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError(
                {'email': 'Некорректный формат email.'}
            )

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': f'Пользователь с email {email} уже существует.'}
            )

        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
