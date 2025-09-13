from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import numpy as np
from datetime import datetime

from .models import EmergencyPrediction, EmergencyType, SeverityLevel
from .ml_models import EmergencyPredictor
from .serializers import PredictionSerializer

# Initialize predictor
predictor = EmergencyPredictor()

class PredictView(APIView):
    def post(self, request):
        try:
            data = request.data
            
            # Extract features
            features = [
                data.get('temperature', 25),
                data.get('humidity', 50),
                data.get('air_quality', 50),
                data.get('wind_speed', 5),
                data.get('precipitation', 2),
                data.get('population_density', 500),
                data.get('building_density', 0.5),
                data.get('hour_of_day', datetime.now().hour),
                data.get('day_of_week', datetime.now().weekday()),
                1 if data.get('is_holiday', False) else 0,
                datetime.now().month,
                datetime.now().timetuple().tm_yday
            ]
            
            # Make prediction
            emergency_type, confidence, probabilities = predictor.predict(features)
            severity = predictor.get_severity(emergency_type, confidence)
            
            # Save prediction to database
            prediction = EmergencyPrediction.objects.create(
                temperature=data.get('temperature', 25),
                humidity=data.get('humidity', 50),
                air_quality=data.get('air_quality', 50),
                wind_speed=data.get('wind_speed', 5),
                precipitation=data.get('precipitation', 2),
                population_density=data.get('population_density', 500),
                building_density=data.get('building_density', 0.5),
                hour_of_day=data.get('hour_of_day', datetime.now().hour),
                day_of_week=data.get('day_of_week', datetime.now().weekday()),
                is_holiday=data.get('is_holiday', False),
                predicted_emergency=emergency_type,
                severity=severity,
                confidence=confidence,
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                location_name=data.get('location_name', '')
            )
            
            # Prepare response
            response_data = {
                'emergency_type': emergency_type,
                'severity': severity,
                'confidence': float(confidence),
                'probabilities': {
                    emergency: float(prob) for emergency, prob in 
                    zip(predictor.label_encoder.classes_, probabilities)
                },
                'prediction_id': prediction.id,
                'timestamp': prediction.timestamp.isoformat(),
                'recommendations': self.get_recommendations(emergency_type, severity)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_recommendations(self, emergency_type, severity):
        """Get recommendations based on emergency type and severity"""
        recommendations = []
        
        if emergency_type == 'fire' and severity in ['high', 'critical']:
            recommendations = [
                "Activate fire alarm system",
                "Evacuate the area immediately",
                "Contact fire department: 911",
                "Close all fire doors and dampers",
                "Shut down HVAC systems if safe to do so"
            ]
        elif emergency_type == 'accident' and severity in ['medium', 'high']:
            recommendations = [
                "Secure the accident area",
                "Provide first aid if trained",
                "Contact emergency services: 911",
                "Document the incident for investigation",
                "Preserve evidence for investigation"
            ]
        elif emergency_type == 'medical' and severity in ['low', 'medium']:
            recommendations = [
                "Provide first aid assistance",
                "Contact medical services if needed",
                "Keep the person comfortable",
                "Monitor vital signs if trained",
                "Clear area for emergency responders"
            ]
        elif emergency_type == 'natural_disaster' and severity in ['high', 'critical']:
            recommendations = [
                "Seek immediate shelter",
                "Monitor emergency broadcasts",
                "Follow evacuation routes if advised",
                "Prepare emergency supplies",
                "Check on vulnerable neighbors if safe"
            ]
        else:
            recommendations = [
                "Continue monitoring conditions",
                "Review emergency procedures",
                "Ensure communication systems are operational",
                "Conduct regular safety checks",
                "Update emergency contact information"
            ]
        
        return recommendations

class BatchPredictView(APIView):
    def post(self, request):
        try:
            data = request.data
            records = data.get('records', [])
            
            results = []
            for record in records:
                features = [
                    record.get('temperature', 25),
                    record.get('humidity', 50),
                    record.get('air_quality', 50),
                    record.get('wind_speed', 5),
                    record.get('precipitation', 2),
                    record.get('population_density', 500),
                    record.get('building_density', 0.5),
                    record.get('hour_of_day', datetime.now().hour),
                    record.get('day_of_week', datetime.now().weekday()),
                    1 if record.get('is_holiday', False) else 0,
                    datetime.now().month,
                    datetime.now().timetuple().tm_yday
                ]
                
                emergency_type, confidence, _ = predictor.predict(features)
                severity = predictor.get_severity(emergency_type, confidence)
                
                results.append({
                    'emergency_type': emergency_type,
                    'severity': severity,
                    'confidence': float(confidence),
                    'location': record.get('location_name', 'Unknown')
                })
            
            return Response({'predictions': results}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PredictionHistoryView(APIView):
    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 100))
            emergency_type = request.GET.get('emergency_type')
            severity = request.GET.get('severity')
            
            queryset = EmergencyPrediction.objects.all()
            
            if emergency_type:
                queryset = queryset.filter(predicted_emergency=emergency_type)
            if severity:
                queryset = queryset.filter(severity=severity)
            
            predictions = queryset.order_by('-timestamp')[:limit]
            serializer = PredictionSerializer(predictions, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Template views
def index(request):
    return render(request, 'prediction/index.html')

def predict_page(request):
    return render(request, 'prediction/predict.html')

def dashboard(request):
    return render(request, 'prediction/dashboard.html')

def result(request):
    return render(request,'prediction/result.html')