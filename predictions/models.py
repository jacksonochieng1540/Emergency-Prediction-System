from django.db import models
from django.contrib.auth.models import User

class EmergencyType(models.TextChoices):
    FIRE = 'fire', 'Fire'
    ACCIDENT = 'accident', 'Accident'
    MEDICAL = 'medical', 'Medical'
    NATURAL_DISASTER = 'natural_disaster', 'Natural Disaster'
    NONE = 'none', 'None'

class SeverityLevel(models.TextChoices):
    NONE = 'none', 'None'
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'

class EmergencyPrediction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()
    humidity = models.FloatField()
    air_quality = models.FloatField()
    wind_speed = models.FloatField()
    precipitation = models.FloatField()
    population_density = models.FloatField()
    building_density = models.FloatField()
    hour_of_day = models.IntegerField()
    day_of_week = models.IntegerField()
    is_holiday = models.BooleanField(default=False)
    
    # Prediction results
    predicted_emergency = models.CharField(
        max_length=20,
        choices=EmergencyType.choices,
        default=EmergencyType.NONE
    )
    severity = models.CharField(
        max_length=10,
        choices=SeverityLevel.choices,
        default=SeverityLevel.NONE
    )
    confidence = models.FloatField(default=0.0)
    
    # Location data (optional)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['predicted_emergency']),
            models.Index(fields=['severity']),
        ]

class PredictionFeedback(models.Model):
    prediction = models.ForeignKey(EmergencyPrediction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField()
    actual_emergency = models.CharField(
        max_length=20,
        choices=EmergencyType.choices,
        null=True,
        blank=True
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MLModelVersion(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    training_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    model_file = models.FileField(upload_to='ml_models/')
    
    class Meta:
        unique_together = ['name', 'version']