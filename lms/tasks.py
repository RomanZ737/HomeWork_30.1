from celery import shared_task
from django.core.mail import send_mail
from users.models import CustomUser
from config import settings
from datetime import timezone, timedelta


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
    """
    Проверяет пользователей по дате последнего входа.
    Если пользователь не заходил более 30 дней - блокируем.
    """
    users = CustomUser.objects.all()
    for user in users:
        if user.last_login:
            if  timezone.now() - user.last_login > timedelta(days=30):
                user.is_active = False
                user.save()
        else:
            if timezone.now() - user.date_joined > timedelta(days=30):
                user.is_active = False
                user.save()