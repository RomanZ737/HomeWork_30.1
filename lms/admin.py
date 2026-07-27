from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview', 'description')
    list_filter = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'description')
    list_filter = ('name', 'course')
    search_fields = ('name', 'course')
