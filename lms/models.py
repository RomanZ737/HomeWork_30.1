from django.db import models
from config import settings

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name='Course name', help_text='Название курса')
    preview = models.ImageField(upload_to='img/course_preview/', null=True, blank=True)
    description = models.TextField(verbose_name='Course description', null=True, blank=True, help_text='Описание курса')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField(verbose_name='Course price')

    class Meta:
        ordering = ['name']
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return f'{self.name}, {self.description}'


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Lesson name', help_text='Название урока')
    description = models.TextField(verbose_name='Lesson description', null=True, blank=True, help_text='Описание урока')
    preview = models.ImageField(upload_to='img/lesson_preview/', null=True, blank=True)
    video_url = models.CharField(max_length=100, verbose_name='Lesson video link', help_text='Ссылка на видео', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    price = models.IntegerField(verbose_name='Course price')

    class Meta:
        ordering = ['name']
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return f'{self.name}, {self.description}'


class CourseUpdateSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'course')