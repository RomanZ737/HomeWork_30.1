from rest_framework import serializers
from .models import Course, Lesson, CourseUpdateSubscription
from .validators import validate_video_url, validate_description


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.CharField(validators=[validate_video_url])

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lesson_set = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()
    description = serializers.CharField(validators=[validate_description])
    subscription = serializers.SerializerMethodField()

    def get_subscription(self, obj):
        request = self.context.get('request')
        if CourseUpdateSubscription.objects.filter(course_id=obj.id, user=request.user).exists():
            return 'Подписан'
        else:
            return 'Не подписан'

    def get_lesson_count(self, obj):
        return obj.lesson_set.count()


    class Meta:
        model = Course
        fields = ('name', 'lesson_set', 'description', 'lesson_count', 'id', 'owner', 'subscription')

