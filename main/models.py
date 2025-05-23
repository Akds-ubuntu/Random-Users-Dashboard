from django.db import models
from django.urls import reverse


class DisplayedManager(models.Manager):
    """
    Менеджер, возвращающий пользователей, отсортированных по убыванию id.
    Используется для отображения последних добавленных пользователей первыми.
    """
    def get_queryset(self):
        return super().get_queryset().order_by('-pk')


class RandomUser(models.Model):
    """
    Модель пользователя, полученного из внешнего API randomuser.me.
    """
    gender = models.CharField(max_length=20, verbose_name="Пол")
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    location = models.JSONField(
        default=dict, verbose_name='Данные о месте жительства'
    )
    email = models.EmailField(max_length=100, verbose_name='Почта')
    phone = models.CharField(max_length=100, verbose_name='Номер телефона')
    picture = models.URLField(verbose_name='Фото')

    objects = models.Manager()
    displayed = DisplayedManager()

    def get_absolute_url(self):
        """
        Возвращает абсолютный URL для
        просмотра пользователя (используется в шаблонах).
        """
        return reverse('user', kwargs={'user_pk': self.pk})

    def __str__(self):
        return self.first_name
