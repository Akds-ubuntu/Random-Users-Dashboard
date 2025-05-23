import logging

import requests
from django.db import transaction
from rest_framework.exceptions import ValidationError

from main.models import RandomUser
from main.serializers import RandomUserSerializer

logger = logging.getLogger(__name__)


class RandomUserService:
    """
    Сервисный класс для загрузки,
    валидации и сохранения случайных пользователей
    с использованием внешнего API randomuser.me.
    """
    _shared_session = None
    BASE_URL_API = 'https://randomuser.me/api/'
    DEFAULT_BATCH_SIZE = 1000

    def __init__(self):
        if RandomUserService._shared_session is None:
            RandomUserService._shared_session = requests.Session()
        self.session = RandomUserService._shared_session

    def fetch_users(self, count=1):
        """
        # Формируем параметры запроса к API
        # 'inc' — список полей, которые нужно получить
        # 'results' — количество пользователей в ответе
        # 'noinfo' — отключение метаинформации
        """
        base_params = {
            'inc': 'gender,name,phone,email,location,picture',
            'results': count,
            'noinfo': True
        }

        try:
            response = self.session.get(
                RandomUserService.BASE_URL_API, params=base_params, timeout=10
            )
            response.raise_for_status()
            data = response.json()['results']
            return data
        except requests.ConnectionError:
            logger.error("No internet connection")
            raise
        except requests.Timeout:
            logger.error('Request timed out')
            raise
        except requests.RequestException as e:
            logger.error(f'API request failed: {e}')
            raise

        except (KeyError, ValueError) as e:
            logger.error(f'Invalid API response: {e}')
            raise

    @transaction.atomic
    def save_users(self, users_data):
        """
        Сохраняем данные в DB
        """
        users = []
        for user_data in users_data:
            try:
                users.append(self._create_user(user_data))
            except ValidationError as e:
                logger.warning(f'Invalid user data: {e}')
                continue
        try:
            if users:
                created = RandomUser.objects.bulk_create(users)
                return len(created)
            return 0
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise

    def load_initial_users(self, total=1000):
        """
        Основной метод для взаимодействия с данным сервисом
        """

        remaining = total

        while remaining > 0:

            current_size = min(remaining, RandomUserService.DEFAULT_BATCH_SIZE)
            try:

                data = self.fetch_users(current_size)
                saved_count = self.save_users(data)
                remaining -= saved_count or 0
                logger.info(
                    f"Saved { saved_count} users, {remaining} remaining"
                )

                if saved_count == 0:
                    raise RuntimeError("No users saved in last batch")
            except RuntimeError as e:
                logger.warning(f"No users saved in last batch, stopping{e}")
                break
            except Exception as e:
                logger.error(f"Batch failed: {e}")
                break

    def _create_user(self, user_data):
        """
        Вальдируем данные пользователя с помощью DRF-сериализатора.
        Возвращаем объект модели без сохранения (используется в bulk_create).
        """
        serializer = RandomUserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)

        return RandomUser(**serializer.validated_data)
