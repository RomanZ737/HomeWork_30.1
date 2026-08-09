import os

from stripe import StripeClient, error
from dotenv import load_dotenv
from rest_framework import serializers

load_dotenv()


def stripe_payment(payment):
    """Выполняем запрос ссылки на оплату."""
    try:
        client = StripeClient(os.environ.get('STRIPE_SECRET_KEY'))

        # Создаём продукт
        product = client.v1.products.create({
            "name": payment.payed_course.name,
        })

        # Создаём цену
        price = client.v1.prices.create({
            "currency": "rub",
            "unit_amount": payment.payment_amount * 100,
            "product": product.id,
        })

        # Создаём сессию
        session = client.v1.checkout.sessions.create({
            'success_url': 'http://localhost:8000/payment/success',
            'cancel_url': 'http://localhost:8000/payment/cancel',
            "line_items": [{"price": price.id, "quantity": 1}],
            "mode": "payment",
        })

        return session

    except error.CardError as e:
        raise serializers.ValidationError(
            {'payment': f'Ошибка карты: {e.user_message}'}
        )
    except error.RateLimitError as e:
        raise serializers.ValidationError(
            {'payment': 'Слишком много запросов. Попробуйте позже.'}
        )
    except error.InvalidRequestError as e:
        raise serializers.ValidationError(
            {'payment': f'Неверный запрос: {e.user_message}. Параметр: {e.param}'}
        )
    except error.AuthenticationError as e:
        raise serializers.ValidationError(
            {'payment': 'Ошибка аутентификации Stripe. Проверьте ключ.'}
        )
    except error.APIConnectionError as e:
        raise serializers.ValidationError(
            {'payment': 'Ошибка соединения с платёжным сервисом.'}
        )
    except error.StripeError as e:
        raise serializers.ValidationError(
            {'payment': f'Ошибка Stripe ({e.http_status}): {e.user_message}'}
        )
    except Exception as e:
        raise serializers.ValidationError(
            {'payment': f'Неизвестная ошибка: {str(e)}'}
        )



def get_stripe_session_status(session_id):
    """Получает статус сессии из Stripe."""
    client = StripeClient(os.environ.get('STRIPE_SECRET_KEY'))

    try:
        session = client.v1.checkout.sessions.retrieve(session_id)
        return {
            'status': session.payment_status,
            'payment_status': session.payment_status,
        }
    except Exception as e:
        return {'error': str(e)}