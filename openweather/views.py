from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

API_KEY = settings.API_KEY
import requests
from rest_framework.response import Response
from .serializers import WeatherSerializer
from rest_framework import status
from .models import Weather

def index(request):
    return HttpResponse('My weather app is running!')

class WeatherByCity(APIView):
    """
    post: 
    Fetches weather data for a given city from the OpenWeatherMap API and saves it to the database.
    
    Request body: {"city": "city_name"}
    Response body: {
        city, temperature, humidity, pressure, description, wind_speed, country
    }
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'city': openapi.Schema(type=openapi.TYPE_STRING, description='City name'),
            },
        ),
        responses={
            200: openapi.Response(
                description="Weather data",
                schema=WeatherSerializer(),
            ),
            400: "Bad Request",
            404: "City not found",
        },
    )
    
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
    
class WeatherData(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Weather data",
                schema=WeatherSerializer(many=True),
            ),
        },
    )
    
    def get(self, request):
        weather_data = Weather.objects.all()
        serializer = WeatherSerializer(weather_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)