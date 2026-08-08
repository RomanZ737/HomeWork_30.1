from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from .models import Course, Lesson, CourseUpdateSubscription


class LessonTestCase(APITestCase):
    def setUp(self):

        # Обычный пользователь
        self.user = CustomUser.objects.create_user(
            email='test_user_1@example.com',
            password='user12345@',
            city='Moscow',
            phone_number='+79991111111'
        )

        # Другой пользователь (не владелец)
        self.other_user = CustomUser.objects.create_user(
            email='test_user_2@example.com',
            password='user12345@',
            city='St. Petersburg',
            phone_number='+79992222222'
        )

        # курсы
        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание курса',
            owner=self.user
        )

        self.other_course = Course.objects.create(
            name='Чужой курс',
            description='Описание чужого курса',
            owner=self.other_user
        )

        # урок
        self.lesson = Lesson.objects.create(
            course=self.course,
            name='Тестовый урок',
            description='Описание урока',
            video_url='https://youtube.com/',
            owner=self.user
        )

        self.other_lesson = Lesson.objects.create(
            course=self.other_course,
            name='Чужой урок',
            description='Описание чужого урока',
            video_url='https://youtube.com/',
            owner=self.other_user
        )

        # Аутентификация
        self.client.force_authenticate(user=self.user)


class LessonCreateTest(LessonTestCase):
    """Тесты на создание урока."""

    def test_create_lesson_success(self):
        data = {
            'course': self.course.id,
            'name': 'Новый урок',
            'description': 'Описание нового урока',
            'video_url': 'https://youtube.com/',
        }

        response = self.client.post('/lesson/create/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Новый урок')


    def test_create_lesson_invalid_url(self):
        """Создание урока с запрещённой ссылкой"""
        data = {
            'course': self.course.id,
            'name': 'Урок с плохой ссылкой',
            'description': 'Описание',
            'video_url': 'https://xxxxxx.com/',
        }

        response = self.client.post('/lesson/create/', data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_lesson_no_auth(self):
        """без аутентификации"""
        self.client.force_authenticate(user=None)

        data = {
            'course': self.course.id,
            'name': 'Неавторизованный урок',
            'video_url': 'https://youtube.com/'
        }

        response = self.client.post('/lesson/create/', data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LessonListTest(LessonTestCase):
    """Тесты на получение списка уроков."""

    def test_list_lessons_owner(self):
        """Владелец"""
        response = self.client.get('/lesson/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for lesson in response.data['results']:
            self.assertEqual(lesson['owner'], self.user.id)

    def test_list_lessons_no_auth(self):
        """без аутентификации."""
        self.client.force_authenticate(user=None)

        response = self.client.get('/lesson/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LessonRetrieveTest(LessonTestCase):
    """Тесты на получение одного урока."""

    def test_retrieve_own_lesson(self):
        """Просмотр своего урока."""
        response = self.client.get(f'/lesson/{self.lesson.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lesson.name)

    def test_retrieve_other_lesson(self):
        """Просмотр чужого урока"""
        response = self.client.get(f'/lesson/{self.other_lesson.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_nonexistent_lesson(self):
        """несуществующий урок"""
        response = self.client.get('/lesson/9999/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LessonUpdateTest(LessonTestCase):
    """Тесты на обновление урока."""

    def test_update_own_lesson(self):
        data = {
            'name': 'Обновлённый урок',
            'description': 'Новое описание',
        }

        response = self.client.patch(
            f'/lesson/update/{self.lesson.id}/',
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Обновлённый урок')

    def test_update_other_lesson(self):
        """Обновление чужого урока (должен быть запрещён)."""
        data = {'name': 'Взломанный урок'}

        response = self.client.patch(
            f'/lesson/update/{self.other_lesson.id}/',
            data=data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonDeleteTest(LessonTestCase):
    """Тесты на удаление урока."""

    def test_delete_own_lesson(self):
        """Удаление своего урока."""
        response = self.client.delete(f'/lesson/delete/{self.lesson.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_delete_other_lesson(self):
        """Удаление чужого урока (должен быть запрещён)."""
        response = self.client.delete(
            f'/lesson/delete/{self.other_lesson.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)


class SubscriptionTest(LessonTestCase):
    """Тесты на подписку на обновления курса."""

    def test_subscribe_to_course(self):
        """Подписка на курс."""
        data = {'course_id': self.course.id}

        response = self.client.post('/subscription/', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(
            CourseUpdateSubscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

    def test_unsubscribe_from_course(self):
        """Отписка от курса."""
        # Сначала подписываемся
        CourseUpdateSubscription.objects.create(
            user=self.user,
            course=self.course
        )

        data = {'course_id': self.course.id}
        response = self.client.post('/subscription/', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(
            CourseUpdateSubscription.objects.filter(
                user=self.user,
                course=self.course
            ).exists()
        )

    def test_subscribe_nonexistent_course(self):
        """Подписка на несуществующий курс."""
        data = {'course_id': 9999}

        response = self.client.post('/subscription/', data=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_no_auth(self):
        """Подписка без аутентификации."""
        self.client.force_authenticate(user=None)

        data = {'course_id': self.course.id}
        response = self.client.post('/subscription/', data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionInCourseTest(LessonTestCase):
    """Тесты на признак подписки в выдаче курсов."""

    def test_course_shows_subscription_status(self):
        """Курс показывает статус подписки."""
        # Подписываемся на курс
        CourseUpdateSubscription.objects.create(
            user=self.user,
            course=self.course
        )

        response = self.client.get(f'/lms/{self.course.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscription'], 'Подписан')

    def test_course_shows_no_subscription(self):
        """Курс показывает отсутствие подписки."""
        response = self.client.get(f'/lms/{self.course.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscription'], 'Не подписан')


class ModeratorTest(LessonTestCase):
    """Тесты для модератора."""

    def setUp(self):
        super().setUp()

        # Создаём модератора и группу
        from django.contrib.auth.models import Group
        self.moderator_group = Group.objects.create(name='Moderators')

        self.moderator = CustomUser.objects.create_user(
            email='moderator@example.com',
            password='moderator123@'
        )
        self.moderator.groups.add(self.moderator_group)

        self.client.force_authenticate(user=self.moderator)

    def test_moderator_can_view_all_lessons(self):
        """Модератор видит все уроки."""
        response = self.client.get('/lesson/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_moderator_cannot_create_lesson(self):
        """Модератор не может создавать уроки."""
        data = {
            'course': self.course.id,
            'name': 'Урок от модератора',
            'video_url': 'https://youtube.com/'

        }

        response = self.client.post('/lesson/create/', data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_delete_lesson(self):
        """Модератор не может удалять уроки."""
        response = self.client.delete(f'/lesson/delete/{self.lesson.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)