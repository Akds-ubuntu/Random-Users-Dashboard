from django import forms


class FormNumber(forms.Form):
    """Форма для валидации числа случайных юзеров"""
    number = forms.IntegerField(
        min_value=0, max_value=1000, label='Число новых людей'
    )
