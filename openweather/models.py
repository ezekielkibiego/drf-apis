from django.db import models

class Weather(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=255)
    date_time = models.DateTimeField(auto_now_add=True)
    pressure = models.FloatField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city} - {self.temperature}°C"
    