from django.urls import path
from .views import UserCreateView, UserUpdateView, UserDeleteView, UserLoginView, UserLogoutView

app_name = "user"

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]
