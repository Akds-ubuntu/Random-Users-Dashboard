import logging
import random

from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from main.forms import FormNumber
from main.models import RandomUser
from main.services import RandomUserService

logger = logging.getLogger(__name__)


class UsersView(FormMixin, ListView):
    """Отображает список пользователей с пагинацией и формой загрузки новых."""

    template_name = 'main/user_list.html'
    context_object_name = 'user_list'
    form_class = FormNumber
    success_url = reverse_lazy('main')
    paginate_by = 10

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос с формой."""
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Обрабатывает валидную форму и загружает пользователей."""
        number = form.cleaned_data['number']
        RandomUserService().load_initial_users(total=number)
        return super().form_valid(form)

    def get_queryset(self):
        """
        Возвращает queryset пользователей, отсортированных по id.
        Используется для отображения на странице списка.
        """
        return RandomUser.displayed.all()


class ShowUserView(DetailView):
    """Отображает профиль пользователя по pk из URL."""
    model = RandomUser
    template_name = 'main/user.html'
    pk_url_kwarg = 'user_pk'
    context_object_name = 'user'


class RandomUserView(DetailView):
    """Отображает случайного пользователя из DB."""
    model = RandomUser
    template_name = 'main/user.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        """Метод для получения случайного объекта пользователя."""
        try:
            ids = list(RandomUser.objects.values_list('id', flat=True))
            if not ids:
                raise Http404("No users available")
            random_id = random.choice(ids)
            return RandomUser.objects.get(pk=random_id)
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise Http404("No users available")
