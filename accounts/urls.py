from django.urls import path, include
from .views import index, register, login
urlpatterns = [
    path('', index, name='index'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
]