from . import views
from django.urls import path


urlpatterns = [
    path('', views.UsersView.as_view(), name='main'),
    path('<int:user_pk>/', views.ShowUserView.as_view(), name='user'),
    path('random/', views.RandomUserView.as_view(), name='random_user'),
]
