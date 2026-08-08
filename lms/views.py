from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, HttpResponse
from .models import Course, Lesson, CourseUpdateSubscription
from .permissions import IsOwnerOrModerator, IsOwner, IsNotModerator
from .serializers import CourseSerializer, LessonSerializer
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from .paginators import CoursePaginator, LessonPaginator


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)


    def perform_create(self, serializer):
        new_course = serializer.save()
        new_course.owner = self.request.user
        new_course.save()



    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsNotModerator()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsOwner()]
        if self.action in ("update", "partial_update", "retrieve"):
            return [IsAuthenticated(), IsOwnerOrModerator()]
        return [IsAuthenticated()]



class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsNotModerator]

    def perform_create(self, serializer):
        new_lesson = serializer.save()
        new_lesson.owner = self.request.user
        new_lesson.save()


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Moderators').exists():
            return Lesson.objects.all()  # модератор видит всё
        return Lesson.objects.filter(owner=user)  # обычный юзер — только свои


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class CourseSubscription(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id')
        course_item = get_object_or_404(Course, pk=course_id)
        subs_item = CourseUpdateSubscription.objects.filter(course=course_item, user=user)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            CourseUpdateSubscription.objects.create(
                                course=course_item,
                                user=user
                                )
            message = 'подписка добавлена'
        return Response({"message": message})
