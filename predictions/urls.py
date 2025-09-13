from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('predict/', views.predict_page, name='predict_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('result/', views.result, name='result'),
    
    
    # API endpoints
    path('api/predict/', views.PredictView.as_view(), name='api_predict'),
    path('api/batch_predict/', views.BatchPredictView.as_view(), name='api_batch_predict'),
    path('api/history/', views.PredictionHistoryView.as_view(), name='api_history'),
]