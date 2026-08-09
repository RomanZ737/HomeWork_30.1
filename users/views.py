from warnings import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import CustomUser, Payments
from .permissions import IsOwner
from .serializers import CustomUserSerializer, PaymentsSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from lms.models import Course
from .services import stripe_payment, get_stripe_session_status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsOwner()]
        return super().get_permissions()




class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('payed_lesson', 'payed_course', 'payment_method')
    ordering_fields = ('payment_at',)

    def create(self, request, *args, **kwargs):
        """
                Создание платежа и получение ссылки на оплату Stripe.

                Тело запроса:
                - payed_course (int, обязательный): ID курса для оплаты

                Ответы:
                - 201: платёж создан, возвращает ссылку на оплату
                - 400: неверные параметры
                - 401: не авторизован
                """

        course_id = request.data.get('payed_course')
        course_item = get_object_or_404(Course, pk=course_id)

        # Создаём платёж
        payment = Payments.objects.create(
            user=request.user,
            payed_course=course_item,
            payment_amount=course_item.price
        )

        # получаем ссылку
        session = stripe_payment(payment)
        payment.payment_link = session.url
        payment.stripe_session_id = session.id
        payment.save(update_fields=['payment_link', 'stripe_session_id'])

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




    @action(detail=False, methods=['get'], url_path='status/(?P<session_id>[^/.]+)')
    def payment_status(self, request, session_id=None):
        """
        Проверка статуса платежа по Stripe session_id.

        Параметры пути:
        - session_id (str): ID сессии Stripe

        Ответы:
        - 200: статус платежа (paid/unpaid/pending)
        - 404: платёж с таким session_id не найден
        """

        stripe_status = get_stripe_session_status(session_id)

        # Обновляем статус в БД
        try:
            payment = Payments.objects.get(stripe_session_id=session_id)
            if stripe_status.get('payment_status') == 'paid':
                payment.payment_status = 'paid'
                payment.save(update_fields=['payment_status'])
            elif stripe_status.get('payment_status') == 'unpaid':
                payment.payment_status = 'pending'
                payment.save(update_fields=['payment_status'])
        except Payments.DoesNotExist:
            pass

        return Response(stripe_status)



    # def perform_create(self, serializer):
    #     # Сохраняем платёж
    #     course = serializer.validated_data.get('payed_course')
    #     payment = serializer.save(user=self.request.user,
    #                               payment_amount=course.price)
    #
    #     # сохраняем ссылку
    #     payment_link = stripe_payment(payment)
    #     payment.payment_link = payment_link
    #     payment.save(update_fields=['payment_link'])

    # def post(self, request):
    #     course_id = request.data.get('course_id')
    #     course_item = get_object_or_404(Course, pk=course_id)
    #
    #     # Создаём платёж
    #     payment = Payments.objects.create(
    #         user=request.user,
    #         payed_course=course_item,
    #         payment_amount=course_item.price
    #     )
    #
    #     # создаём ссылку
    #     payment_link = stripe_payment(payment)
    #     payment.payment_link = payment_link
    #     payment.save(update_fields=['payment_link'])
    #
    #     serializer = PaymentsSerializer(payment)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)




class UserCreateAPIView(CreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)

