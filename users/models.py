from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from lms.models import Lesson, Course


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    username = models.CharField(max_length=150, blank=True, null=True, unique=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to="img/avatar/", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class PaymentType(models.TextChoices):
    CASH = 'Cash', 'Наличные'
    TRANSFER = 'Transfer', 'Перевод'


class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Ожидает оплаты'
    PAID = 'Paid', 'Оплачен'
    CANCELLED = 'Cancelled', 'Отменён'


class Payments(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             verbose_name='User that payd for the course',
                             help_text='Пользователь, который оплатил курс')
    payment_at = models.DateTimeField(default=timezone.now, verbose_name='Date/Time of payment')
    payed_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    payed_course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    payment_amount = models.PositiveIntegerField(default=0, verbose_name='Payment Amount')
    payment_method = models.CharField(choices=PaymentType, default=PaymentType.TRANSFER)
    payment_link = models.URLField(max_length=500, blank=True, null=True)
    stripe_session_id = models.CharField(max_length=200, blank=True, null=True)
    payment_status = models.CharField(
        max_length=50,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    def __str__(self):
        return f'{self.user} {self.payed_lesson if self.payed_lesson else self.payed_course} {self.payment_amount}'

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_at']
