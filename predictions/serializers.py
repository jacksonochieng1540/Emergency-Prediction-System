from rest_framework import serializers
from .models import EmergencyPrediction, PredictionFeedback

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyPrediction
        fields = '__all__'

class PredictionFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionFeedback
        fields = '__all__'