from rest_framework import serializers
from main.models import RandomUser


class RandomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для преобразования данных внешнего API randomuser.me
    в формат, совместимый с моделью RandomUser.
    """

    class Meta:
        model = RandomUser
        fields = [
            'gender', 'first_name', 'last_name',
            'phone', 'email', 'location', 'picture'
        ]

    def _validate_nested_field(self, data, field_name, required_keys):
        """
        Проверяет наличие вложенного словаря и необходимых ключей в нём.
        Используется для валидации полей name и picture из API.
        """
        nested = data.get(field_name)
        if not isinstance(nested, dict):
            raise serializers.ValidationError(
                {field_name: f"Expected dict with keys {required_keys}"}
            )
        missing_keys = [k for k in required_keys if k not in nested]
        if missing_keys:
            raise serializers.ValidationError(
                {field_name: f"Missing keys: {missing_keys}"}
            )
        return nested

    def to_internal_value(self, data):
        """
        Переопределение метода, чтобы распарсить вложенные поля внешнего API:
        - name.first/last → first_name/last_name
        - picture.thumbnail → picture
        Также валидируются обязательные поля.
        """
        data = data.copy()

        required_fields = [
            'gender', 'name', 'phone', 'email', 'location', 'picture'
        ]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise serializers.ValidationError(
                {field: ["This field is required."] for field in missing}
            )

        name = self._validate_nested_field(data, "name", ["first", "last"])
        picture = self._validate_nested_field(data, "picture", ["thumbnail"])

        data["first_name"] = name.get("first")
        data["last_name"] = name.get("last")
        data["picture"] = picture.get("thumbnail")

        return super().to_internal_value(data)

    def validate_location(self, value):
        """
        Простая валидация для поля location: должен быть словарём.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("location must be a dict")
        return value
