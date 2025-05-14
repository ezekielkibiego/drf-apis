from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
API_KEY = settings.API_KEY
import requests
from rest_framework.response import Response
from .serializers import WeatherSerializer
from rest_framework import status
from .models import Weather

def index(request):
    return HttpResponse('My weather app is running!')

class WeatherByCity(APIView):
    def post(self, request):
        city = request.data.get('city')
        if not city:
            return Response({'error': 'City name is required'}, status=400)
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return Response({'error': 'City not found'}, status=response.status_code)
        
        data = response.json()
        
        weather = Weather.objects.create(
            city=data['name'],
            temperature=data['main']['temp'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure'],
            description=data['weather'][0]['description'],
            wind_speed=data['wind']['speed'],
            country=data['sys']['country']
        )
        
        serilizer = WeatherSerializer(weather)
        return Response(serilizer.data, status=status.HTTP_200_OK)