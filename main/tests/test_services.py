import logging
from unittest.mock import patch, MagicMock

from django.db import DatabaseError
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from main.services import RandomUserService
import requests


class RandomUserServiceTest(TestCase):

    def setUp(self):
        self.service = RandomUserService()
        self.mock_user_data = {
            'gender': 'male',
            'name': {'first': 'John', 'last': 'Doe'},
            'phone': '123-456-7890',
            'email': 'john.doe@example.com',
            'location': {'city': 'New York', 'country': 'USA'},
            'picture': {'thumbnail': 'http://example.com/thumb.jpg'}
        }
        self.error_mock_data = {
            'error': (
                "Uh oh, something has gone wrong. "
                "Please tweet us @randomapi about the issue. Thank you."
            )
        }

    @patch('main.services.requests.Session.get')
    def test_fetch_users_success(self, mock_get):
        """Проверка успешного получения пользователей через API."""
        fake_data = {'results': [self.mock_user_data]}
        mock_response = MagicMock()
        mock_response.json.return_value = fake_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.service.fetch_users(1)

        self.assertEqual(result, fake_data['results'])
        mock_get.assert_called_once_with(
            'https://randomuser.me/api/',
            params={
                'inc': 'gender,name,phone,email,location,picture',
                'results': 1,
                'noinfo': True
            },
            timeout=10
        )

    @patch('main.services.requests.Session.get')
    def test_fetch_users_timeout(self, mock_get):
        """Тестирование обработки ошибки таймаута при запросе."""
        mock_get.side_effect = requests.Timeout("Timeout error")

        with self.assertRaises(requests.Timeout):
            self.service.fetch_users(1)

    @patch('main.services.requests.Session.get')
    def test_fetch_users_request_exception(self, mock_get):
        """Тест обработки общих ошибок при выполнении запроса."""
        mock_get.side_effect = requests.RequestException("Some error")

        with self.assertRaises(requests.RequestException):
            self.service.fetch_users(1)

    @patch('main.services.requests.Session.get')
    def test_fetch_users_invalid_json(self, mock_get):
        """Проверка обработки невалидного JSON в ответе API."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            self.service.fetch_users(1)

    @patch('main.services.requests.Session.get')
    def test_fetch_users_empty_result(self, mock_get):
        """Тест обработки пустого результата от API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.service.fetch_users(1)
        self.assertEqual(result, [])

    @patch('main.services.requests.Session.get')
    def test_fetch_users_missing_results_key(self, mock_get):
        """Проверка реакции на отсутствие ключа results в ответе."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(KeyError):
            self.service.fetch_users(1)

    @patch('main.services.requests.Session.get')
    def test_fetch_users_connection_error_logs(self, mock_get):
        """Тестирование логирования ошибок соединения."""
        mock_get.side_effect = requests.ConnectionError("No connection")

        with self.assertLogs('main.services', level='ERROR') as log:
            with self.assertRaises(requests.ConnectionError):
                self.service.fetch_users(1)

        self.assertTrue(
            any("No internet connection" in msg for msg in log.output)
        )

    def test_create_user_success(self):
        """Проверка корректного создания объекта пользователя."""
        user = self.service._create_user(self.mock_user_data)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.gender, 'male')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.phone, '123-456-7890')
        self.assertEqual(user.email, 'john.doe@example.com')
        self.assertEqual(user.location, {'city': 'New York', 'country': 'USA'})

    def test_create_user_invalid_data(self):
        """Тест обработки невалидных данных при создании пользователя."""
        invalid_data = self.mock_user_data.copy()
        invalid_data['name'] = None

        with self.assertRaises(ValidationError):
            self.service._create_user(invalid_data)

    def test_save_users_success(self):
        """Проверка успешного сохранения списка пользователей."""
        count = self.service.save_users([self.mock_user_data])
        self.assertEqual(count, 1)
        from main.models import RandomUser
        self.assertEqual(RandomUser.objects.count(), 1)

    def test_save_users_partial_failure(self):
        """Тест частичного сохранения при наличии невалидных данных."""
        from main.models import RandomUser

        invalid_data = self.mock_user_data.copy()
        invalid_data['name'] = None

        with self.assertLogs('main.services', level='WARNING') as cm:
            count = self.service.save_users(
                [self.mock_user_data, invalid_data]
            )

        self.assertEqual(count, 1)
        self.assertEqual(RandomUser.objects.count(), 1)
        self.assertTrue(any('Invalid user data' in msg for msg in cm.output))

    def test_save_users_empty_list(self):
        """Проверка обработки пустого списка для сохранения."""
        count = self.service.save_users([])
        self.assertEqual(count, 0)

    @patch('main.services.RandomUserService.fetch_users')
    @patch('main.services.RandomUserService.save_users')
    def test_load_initial_users_success(self, mock_save, mock_fetch):
        """Тест успешной загрузки начальных данных."""
        mock_fetch.return_value = [self.mock_user_data]
        mock_save.return_value = 1

        with self.assertLogs('main.services', level='INFO') as cm:
            self.service.load_initial_users(total=3)

        self.assertEqual(mock_fetch.call_count, 3)
        self.assertEqual(mock_save.call_count, 3)
        self.assertTrue(any('Saved 1 users' in msg for msg in cm.output))

    @patch('main.services.RandomUserService.fetch_users')
    @patch('main.services.RandomUserService.save_users')
    def test_load_initial_users_with_error_and_stop(
        self, mock_save, mock_fetch
    ):
        """Тест прерывания загрузки при ошибках."""
        mock_fetch.side_effect = [
            requests.RequestException("API error"),
            [self.mock_user_data],
            [self.mock_user_data],
        ]
        mock_save.side_effect = [0, 1, 0]

        with self.assertLogs('main.services', level='ERROR') as error_logs:
            self.service.load_initial_users(total=1)
        with self.assertLogs('main.services', level='WARNING') as warning_logs:
            self.service.load_initial_users(total=2)

        self.assertEqual(mock_fetch.call_count, 2)
        self.assertEqual(mock_save.call_count, 1)
        self.assertTrue(
            any('Batch failed' in msg for msg in error_logs.output)
        )
        self.assertTrue(
            any(
                'No users saved in last batch' in msg
                for msg in warning_logs.output
            )
        )

    @patch('main.services.RandomUser.objects.bulk_create')
    def test_save_users_bulk_create_fails(self, mock_bulk_create):
        """Проверка обработки ошибок базы данных при сохранении."""
        mock_bulk_create.side_effect = DatabaseError("DB fail")
        with self.assertRaises(DatabaseError):
            self.service.save_users([self.mock_user_data])

    def test_log_appears(self):
        """Тестирование системы логирования сервиса."""
        with self.assertLogs('main.services', level='ERROR') as cm:
            logger = logging.getLogger('main.services')
            logger.error("Test error log")
        self.assertTrue(any("Test error log" in m for m in cm.output))
