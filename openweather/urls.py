from django.urls import path
from .views import index, WeatherByCity, WeatherData

urlpatterns = [
    path('', index, name='index'), 
    path('api/weather/', WeatherByCity.as_view(), name='weather_by_city'), 
    path('api/weather/data/', WeatherData.as_view(), name='weather_data'),
]