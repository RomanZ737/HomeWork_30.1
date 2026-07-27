from .views import (CourseViewSet,
                    LessonCreateAPIView,
                    LessonListAPIView,
                    LessonRetrieveAPIView,
                    LessonUpdateAPIView,
                    LessonDestroyAPIView
                    )
from rest_framework.routers import DefaultRouter
from .apps import LmsConfig

from django.urls import path, include

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r'lms', CourseViewSet, basename='lms')
urlpatterns = [
        path('lesson/create/', LessonCreateAPIView.as_view(), name='create'),
        path('lesson/', LessonListAPIView.as_view(), name='list'),
        path('lesson/<int:pk>/', LessonRetrieveAPIView.as_view(), name='get'),
        path('lesson/update/<int:pk>/', LessonUpdateAPIView.as_view(), name='update'),
        path('lesson/delete/<int:pk>/', LessonDestroyAPIView.as_view(), name='delete'),

              ] + router.urls