from django.test import TestCase
from rest_framework.exceptions import ValidationError
from main.serializers import RandomUserSerializer


class RandomUserSerializerTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'gender': 'male',
            'name': {'first': 'John', 'last': 'Doe'},
            'phone': '123-456-7890',
            'email': 'john.doe@example.com',
            'location': {'city': 'New York', 'country': 'USA'},
            'picture': {'thumbnail': 'http://example.com/thumb.jpg'}
        }
        self.mock_user_data = {
            'gender': 'male',
            'name': {'first': 'John', 'last': 'Doe'},
            'phone': '123-456-7890',
            'email': 'john.doe@example.com',
            'location': {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "country": "USA",
                "postcode": "10001",
                "coordinates": {
                    "latitude": "40.7128", "longitude": "74.0060"
                },
                "timezone": {
                    "offset": "-5:00",
                    "description": "Eastern Time (US & Canada)"
                }
            },
            'picture': {
                'thumbnail': 'http://example.com/thumb.jpg'
            }
        }

    def test_valid_data(self):
        """
        Проверка валидации сериализатора с
        полной валидной структурой данных.
        """
        serializer = RandomUserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_gender(self):
        """
        Проверка, что поле gender обязательно и
        вызывает ошибку при отсутствии.
        """
        data = self.valid_data.copy()
        data.pop('gender')
        serializer = RandomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('gender', serializer.errors)

    def test_name_not_dict(self):
        """Проверка, что поле name должно быть словарём."""
        data = self.valid_data.copy()
        data['name'] = 'not-a-dict'
        serializer = RandomUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_name_missing_keys(self):
        """Проверка, что поле name требует наличия ключей first и last."""
        data = self.valid_data.copy()
        data['name'] = {'first': 'Only'}
        serializer = RandomUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_name(self):
        """Проверка обязательности поля name."""
        data = self.valid_data.copy()
        data.pop('name')
        serializer = RandomUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_phone(self):
        """Проверка обязательности поля phone."""
        data = self.valid_data.copy()
        data.pop('phone')
        serializer = RandomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)

    def test_missing_email(self):
        """Проверка обязательности поля email."""
        data = self.valid_data.copy()
        data.pop('email')
        serializer = RandomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_invalid_email(self):
        """Проверка валидации некорректного формата email."""
        data = self.valid_data.copy()
        data['email'] = 'not-an-email'
        serializer = RandomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_location(self):
        """Проверка обязательности поля location."""
        data = self.valid_data.copy()
        data.pop('location')
        print(data)
        serializer = RandomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('location', serializer.errors)

    def test_location_not_json(self):
        """Проверка, что поле location должно быть словарём."""
        invalid_data = self.mock_user_data.copy()
        invalid_data['location'] = "not a dict"
        serializer = RandomUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('location', serializer.errors)

    def test_picture_not_dict(self):
        """Проверка, что поле picture должно быть словарём."""
        data = self.valid_data.copy()
        data['picture'] = 'not-a-dict'
        serializer = RandomUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_picture_missing_keys(self):
        """Проверка, что поле picture требует наличия ключа thumbnail."""
        data = self.valid_data.copy()
        data['picture'] = {}
        serializer = RandomUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_missing_picture(self):
        """Проверка обязательности поля picture."""
        data = self.valid_data.copy()
        data.pop('picture')
        serializer = RandomUserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_picture_url(self):
        """Проверка валидации некорректного URL в picture.thumbnail."""
        data = self.valid_data.copy()
        data['picture']['thumbnail'] = 'not-a-url'
        serializer = RandomUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('picture', serializer.errors)
