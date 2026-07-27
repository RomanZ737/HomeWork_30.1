from rest_framework import serializers
from .models import Course, Lesson



class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lesson_set = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    def get_lesson_count(self, obj):
        return obj.lesson_set.count()

    class Meta:
        model = Course
        fields = ('name', 'lesson_set', 'description', 'lesson_count')


