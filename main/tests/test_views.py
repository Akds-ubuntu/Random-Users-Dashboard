from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from main.forms import FormNumber
from main.models import RandomUser
from main.services import RandomUserService


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаём тестовых пользователей
        cls.user1 = RandomUser.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            gender='male',
            phone='123-456-789',
            picture='http://example.com/john.jpg',
            location={}
        )
        cls.user2 = RandomUser.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            gender='female',
            phone='987-654-321',
            picture='http://example.com/jane.jpg',
            location={}
        )

    def test_users_view_get(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/user_list.html')
        self.assertContains(response, 'John')
        self.assertContains(response, 'Jane')
        self.assertIsInstance(response.context['form'], FormNumber)
        self.assertEqual(len(response.context['user_list']), 2)

    def test_users_view_post_valid(self):
        with patch.object(
                RandomUserService, 'load_initial_users'
        ) as mock_load:
            response = self.client.post(reverse('main'), {'number': 5})
            self.assertEqual(response.status_code, 302)
            mock_load.assert_called_once_with(total=5)

    def test_users_view_post_invalid(self):
        response = self.client.post(reverse('main'), {'number': 'abc'})

        self.assertEqual(
            response.status_code, 200
        )
        self.assertContains(
            response, 'Введите целое число'
        )

    def test_show_user_view(self):
        response = self.client.get(
            reverse('user', kwargs={'user_pk': self.user1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user1)
        self.assertContains(response, self.user1.first_name)

    def test_show_user_view_404(self):
        response = self.client.get(reverse('user', kwargs={'user_pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_random_user_view(self):
        with patch('random.choice') as mock_rand:
            mock_rand.return_value = self.user2.pk
            response = self.client.get(reverse('random_user'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['user'], self.user2)

    def test_random_user_view_no_users(self):
        RandomUser.objects.all().delete()
        response = self.client.get(reverse('random_user'))
        print(response.status_code)
        self.assertEqual(response.status_code, 404)

    def test_pagination(self):
        for i in range(13):
            RandomUser.objects.create(
                first_name=f'User{i}',
                last_name='Test',
                email=f'user{i}@example.com',
                gender='male',
                phone='000-000-000',
                picture='',
                location={}
            )

        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['user_list']), 10)

    def test_ordering(self):
        response = self.client.get(reverse('main'))
        users = response.context['user_list']
        self.assertEqual(
            users[0], self.user2
        )
