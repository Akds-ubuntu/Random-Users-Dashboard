from django.test import TestCase
from django.urls import reverse
from ..models import RandomUser


class RandomUserModelTest(TestCase):
    def setUp(self):
        self.user1 = RandomUser.objects.create(
            gender='male',
            first_name='John',
            last_name='Doe',
            location={'city': 'New York', 'country': 'USA'},
            email='john@example.com',
            phone='123-456-789',
            picture='http://example.com/john.jpg'
        )
        self.user2 = RandomUser.objects.create(
            gender='female',
            first_name='Jane',
            last_name='Smith',
            location={'city': 'London', 'country': 'UK'},
            email='jane@example.com',
            phone='987-654-321',
            picture='http://example.com/jane.jpg'
        )

    def test_model_creation(self):
        """Проверка создания объекта модели"""
        self.assertEqual(RandomUser.objects.count(), 2)
        self.assertEqual(self.user1.first_name, 'John')
        self.assertEqual(self.user2.email, 'jane@example.com')

    def test_displayed_manager_ordering(self):
        """Проверка кастомного менеджера с сортировкой"""
        displayed_users = RandomUser.displayed.all()
        self.assertEqual(displayed_users[0], self.user2)
        self.assertEqual(displayed_users[1], self.user1)

    def test_get_absolute_url(self):
        """Проверка метода get_absolute_url"""
        url = self.user1.get_absolute_url()
        expected_url = reverse('user', kwargs={'user_pk': self.user1.pk})
        self.assertEqual(url, expected_url)

    def test_string_representation(self):
        """Проверка строкового представления объекта"""
        self.assertEqual(str(self.user1), 'John')
        self.assertEqual(str(self.user2), 'Jane')

    def test_verbose_names(self):
        """Проверка verbose names полей"""
        field_verbose = {
            'gender': 'Пол',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'location': 'Данные о месте жительства',
            'email': 'Почта',
            'phone': 'Номер телефона',
            'picture': 'Фото'
        }

        for field, expected_verbose in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    RandomUser._meta.get_field(field).verbose_name,
                    expected_verbose
                )
