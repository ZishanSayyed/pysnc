from django.urls import path
from .views import (
    LoginView, MeView,
    UserListView, UserCreateView, UserUpdateView
)

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('me/', MeView.as_view()),
     path('users/', UserListView.as_view()),
    path('users/create/', UserCreateView.as_view()),
    path('users/<int:user_id>/', UserUpdateView.as_view()),
]