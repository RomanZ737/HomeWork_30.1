from celery import shared_task
from django.core.mail import send_mail
from users.models import CustomUser
from config import settings
from datetime import timezone, timedelta
from django.db.models import Q


@shared_task
def update_subscription_mail(user_list, course_name):

    send_mail(
        subject=f'Информация по курсу {course_name}',
        message='Ваш курс обновился',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=user_list,
    )


@shared_task
def check_user_last_login():
    now = timezone.now()
    dead_line = now - timedelta(days=30)

    total_users = CustomUser.objects.filter(
        Q(last_login__lt=dead_line) | Q(last_login__isnull=True, date_joined__lt=dead_line)
    ).filter(is_active=True)

    total_users.update(is_active=False)
